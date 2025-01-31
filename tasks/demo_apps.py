from invoke import task
from os.path import join
from subprocess import run
from tasks.util.env import (
    APPS_SOURCE_DIR,
    GHCR_URL,
    GITHUB_ORG,
    LOCAL_REGISTRY_URL,
    print_dotted_line,
)
from tasks.util.nydus import NYDUSIFY_PATH, nydusify

APP_LIST = {
    "helloworld-py": join(APPS_SOURCE_DIR, "helloworld-py"),
    "knative-chaining": join(APPS_SOURCE_DIR, "knative-chaining"),
}


def get_docker_tag_for_app(app_name, nydus=False):
    docker_tag = join(GHCR_URL, GITHUB_ORG, "applications", app_name)
    docker_tag += ":unencrypted"

    if nydus:
        docker_tag += "-nydus"

    return docker_tag


def get_local_registry_tag_for_app(app_name, nydus=False):
    docker_tag = join(LOCAL_REGISTRY_URL, "applications", app_name)
    docker_tag += ":unencrypted"

    if nydus:
        docker_tag += "-nydus"

    return docker_tag


@task
def build(ctx, app=None, nocache=False):
    """
    Build an app for its usage with the project
    """
    if not app:
        app = list(APP_LIST.keys())
    elif app not in APP_LIST:
        print(
            "Unrecognized app name ({}) must be one in: {}".format(app, APP_LIST.keys())
        )
        raise RuntimeError("Unrecognised app name")
    else:
        app = [app]

    for app_name in app:
        app_path = APP_LIST[app_name]

        # First, build the image
        docker_cmd = [
            "docker build",
            "--no-cache" if nocache else "",
            "-t {} .".format(get_docker_tag_for_app(app_name)),
        ]
        docker_cmd = " ".join(docker_cmd)
        run(docker_cmd, shell=True, check=True, cwd=app_path)

        # Second, push it
        docker_cmd = "docker push {}".format(get_docker_tag_for_app(app_name))
        run(docker_cmd, shell=True, check=True)

        # Now, convert it to a nydus image, and push again
        nydusify(
            get_docker_tag_for_app(app_name),
            get_docker_tag_for_app(app_name, nydus=True),
        )


def do_push_to_local_registry(debug=False):
    print_dotted_line("Pushing {} demo apps to local regsitry".format(len(APP_LIST)))

    for app_name in APP_LIST:
        docker_tag = get_docker_tag_for_app(app_name)
        local_registry_tag = get_local_registry_tag_for_app(app_name)

        if debug:
            print(f"Pushing {docker_tag} to {local_registry_tag}...")

        result = run(f"docker pull {docker_tag}", shell=True, capture_output=True)
        assert result.returncode == 0, result.stderr.decode("utf-8").strip()
        if debug:
            print(result.stdout.decode("utf-8").strip())

        result = run(
            f"docker tag {docker_tag} {local_registry_tag}",
            shell=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr.decode("utf-8").strip()
        if debug:
            print(result.stdout.decode("utf-8").strip())

        result = run(
            f"docker push {local_registry_tag}", shell=True, capture_output=True
        )
        assert result.returncode == 0, result.stderr.decode("utf-8").strip()
        if debug:
            print(result.stdout.decode("utf-8").strip())

        # For nydus, we directly use `nydusify copy` as we cannot `docker pull`
        # a nydus image
        result = run(
            "{} copy --source {} --target {} --target-insecure".format(
                NYDUSIFY_PATH,
                get_docker_tag_for_app(app_name, nydus=True),
                get_local_registry_tag_for_app(app_name, nydus=True),
            ),
            shell=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr.decode("utf-8").strip()

    print("Success!")


@task
def push_to_local_registry(ctx, debug=False):
    """
    Build an app for its usage with the project
    """
    do_push_to_local_registry(debug=debug)
