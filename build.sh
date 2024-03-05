#!/bin/bash

command="${1:-build}"
repo_prefix="ghcr.io/genentech"
selected_image_name="${3}"
root_directory=$(pwd)

if [ -n "$2" ]; then
  repo_prefix=$2
fi

declare -A non_root_images=(
  ["./redis"]="spex.redis:latest"
  ["./arango_demo"]="spex.arango.latest"
  ["./omero_demo/database"]="spex.omero.postgresql:latest"
  ["./omero_demo/omeroserver"]="spex.omero.server:latest"
)

declare -A root_images=(
  ["./common"]="spex.common:latest"
  ["./backend"]="spex.backend:latest"
  ["./microservices/ms-omero-sessions"]="spex.omero.sessions:latest"
  ["./microservices/ms-job-manager"]="spex.job.manager:latest"
  ["./microservices/ms-omero-image-downloader"]="spex.omero.image.downloader:latest"
  ["./microservices/ms-pipeline-manager"]="spex.pipeline.manager:latest"
  ["./frontend"]="spex.frontend:latest"
)

if [[ "$command" != "push" && "$command" != "build" ]]; then
  echo "Invalid or no argument supplied. Use 'build' to build only or 'push' to build and push."
  exit 1
fi

echo "Available images to build/push:"
for img in "${non_root_images[@]}" "${root_images[@]}"; do
  echo "- $img"
done

echo "Example usage:"
echo "./build.sh build [repo_prefix] [image_name]"
echo "e.g., ./build.sh build ghcr.io/genentech spex.backend:latest"

set -e

build_and_push() {
  local dir=$1
  local image_name=$2
  local context_path=$3
  local dockerfile_path="$dir/Dockerfile"

  if [ -f "$dir/Demo_Dockerfile" ]; then
    dockerfile_path="$dir/Demo_Dockerfile"
  fi

  if [ -z "$selected_image_name" ] || [ "$selected_image_name" == "$image_name" ]; then
    echo "Processing directory: $dir for image $image_name with Dockerfile: $dockerfile_path in context $context_path"
    docker build -f "$dockerfile_path" -t "$image_name" "$context_path"

    if [ "$command" == "push" ]; then
      docker tag "$image_name" "${repo_prefix}/${image_name//_/\.}"
      docker push "${repo_prefix}/${image_name//_/\.}"
    fi
  else
    echo "Skipping $image_name, not selected."
  fi
}

for dir in "${!non_root_images[@]}"; do
  build_and_push "$dir" "${non_root_images[$dir]}" "$dir"
done

for dir in "${!root_images[@]}"; do
  build_and_push "$dir" "${root_images[$dir]}" "$root_directory"
done

echo "Images ready."
