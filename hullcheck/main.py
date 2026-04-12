import docker
from docker.errors import APIError, ImageNotFound
import logging
from container import recreate_container, recreate_compose_container
from registry import get_remote_data, pull_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            remote_data = get_remote_data(client, image_name)
            if local_digest != remote_data.id:
                logger.info(f"Update available: {container.name}")
                if pull_image(client, image_name):
                    if container.labels.get("com.docker.compose.project"):
                        recreate_compose_container(container)
                    else:
                        recreate_container(container)
            else:
                logger.info(f"{container.name} is up to date")

        except APIError as e:
            logger.error(f"{e.explanation}")
        except ImageNotFound:
            logger.error(f"{image_name} not found in registry")
        except Exception as e:
            logger.error(f"unexpected error: {type(e).__name__}")

    try:
        client.images.prune()
    except APIError as e:
        logger.error(f"{e.explanation}")
    except Exception as e:
        logger.error(f"unexpected error: {type(e).__name__}")


if __name__ == "__main__":
    main()
