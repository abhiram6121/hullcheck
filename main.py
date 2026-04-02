import docker
from docker.errors import APIError, ImageNotFound
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def recreate_container(container):
    logger.warning(f"{container.name} is not Compose managed - manual update required")


def recreate_compose_container(container):
    logger.info(f"Recreating {container.name} via compose")
    service = container.labels.get("com.docker.compose.service")
    workdir = container.labels.get("com.docker.compose.project.working_dir")
    if not service or not workdir:
        logger.warning(f"Docker compose {service} and {workdir} is empty")
        return
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--no-deps", service],
            cwd=workdir,
            check=True,
        )
    except Exception as e:
        logger.error(f"Docker compose failed for {container.name}: {e}")


def main():
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        repo_digests = container.image.attrs["RepoDigests"]

        if not repo_digests:
            logger.debug(f"Skipping {container.name} — local image")
            continue

        if container.image.tags:
            image_name = container.image.tags[0]
        else:
            image_name = container.attrs["Config"]["Image"]

        local_digest = repo_digests[0].split("@")[1]

        try:
            remote_data = client.images.get_registry_data(image_name)
            if local_digest != remote_data.id:
                logger.info(f"Update available: {container.name}")
                try:
                    client.images.pull(image_name)
                    if container.labels.get("com.docker.compose.project"):
                        recreate_compose_container(container)
                    else:
                        recreate_container(container)
                except Exception as e:
                    logger.warning(f"Pull failed for {container.name}: {e}")

                try:
                    client.images.prune()
                except APIError as e:
                    logger.error(f"{e.explanation}")
                except Exception as e:
                    logger.error(f"unexpected error: {type(e).__name__}")

            else:
                logger.info(f"{container.name} is up to date")

        except APIError as e:
            logger.error(f"{e.explanation}")
        except ImageNotFound:
            logger.error(f"{image_name} not found in registry")
        except Exception as e:
            logger.error(f"unexpected error: {type(e).__name__}")


if __name__ == "__main__":
    main()
