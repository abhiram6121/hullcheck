import logging

logger = logging.getLogger(__name__)


def get_remote_data(client, image_name):
    return client.images.get_registry_data(image_name)


def pull_image(client, image_name):
    try:
        client.images.pull(image_name)
        return True
    except Exception as e:
        logger.warning(f"Pull failed for {image_name.split(':')[0]}: {e}")
        return False
