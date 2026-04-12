import logging
import subprocess

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
