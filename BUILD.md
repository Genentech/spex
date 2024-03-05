
# Docker Image Build/Push Script Instructions

This script is used to build and push Docker images to a repository. It accepts up to three arguments: a command (`build` or `push`), a repository prefix (optional), and an image name (optional). Here's a step-by-step guide:

## Running the Script
To use the script, save it to a file, e.g., `build.sh`, and make it executable using the command `chmod +x build.sh`.

## Arguments
- **Command**:
    - `build` to build Docker images.
    - `push` to build and push Docker images to the specified Docker repository.
- **Repository Prefix** (optional): Defaults to `ghcr.io/genentech`, but you can specify a different one as the second argument.
- **Image Name** (optional): If specified, the script will only build/push this image.

## Usage Examples
- To build all images: `./build.sh build`.
- To push all images: `./build.sh push`.
- To build with a different repository prefix: `./build.sh build my.repo.prefix`.
- To build a specific image: `./build.sh build ghcr.io/genentech spex.backend:latest`.

## Key Steps in the Script
- Validates the command (`build` or `push`).
- Lists available images for building/pushing.
- Builds (and pushes, if specified) Docker images based on Dockerfile or Demo_Dockerfile, if available. The build is done in the context of the image directory for non-root images and in the root directory for root images.

## Features
- The script supports images located in the root directory (`root_images`) as well as non-root directories (`non_root_images`).
- Before building/pushing an image, the script checks if a special `Demo_Dockerfile` is available in the image's directory. If so, it is used.

## Completion
After all operations are performed, the script outputs a message indicating the images are ready.

Ensure Docker is installed and running before using this script.
