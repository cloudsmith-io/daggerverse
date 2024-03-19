"""Base for cloudsmith-cli

"""


import time
import typing
from typing import Annotated

import dagger
from dagger import Doc, dag, function, object_type


@object_type
class Cloudsmith:

    @function
    async def push(
            self,
            package_format: str,
            organization: str,
            repository: str,
            package_file: dagger.File,
            api_key: dagger.Secret,
            owner_repo_string: str = "",
            extra_args: list[str] = [],
    ) -> str:
        """Uploads a package to your Cloudsmith repository."""
        ctr = self.base()
        pkgname = await package_file.name()
        ctr = ctr.with_mounted_file(f"/src/{pkgname}", package_file)
        ctr = ctr.with_workdir("/src")

        cmd = ["cloudsmith", "push", f"{package_format}"]

        if owner_repo_string:
            cmd += [owner_repo_string]
        else:
            cmd += [f"{organization}/{repository}"]

        cmd += [pkgname]

        cmd += extra_args

        ctr = ctr.with_env_variable("CLOUDSMITH_API_KEY", await api_key.plaintext())
        return await (
            ctr.with_exec(cmd)
            .stdout()
        )

    @function
    def base(self) -> dagger.Container:
        """Returns a minimal Container with cloudsmith-cli"""
        return (
            dag.container(platform=dagger.Platform("linux/amd64"))
            .from_("python:latest")
            .with_exec(["pip", "install", "--no-cache-dir", "--upgrade", "cloudsmith-cli"])
        ) 
