# AD5M Build cloud setup

Repository: https://github.com/PrettyKitten800/AD5M-Transformation (existing public repository).

The local AD5M Build folder is connected to this remote. A saved Codex Cloud environment named AD5M-Transformation was listed as ready but runnable=false on November 8, 2026. That is not proof that a new cloud task can run. No environment was published by this document.

## Publish a usable environment

In Codex settings > Codex Cloud > Environments, edit the saved AD5M-Transformation environment (or create a current environment using this repository if it is a legacy configuration). Select PrettyKitten800/AD5M-Transformation, main. Ask setup to install native FreeCAD Python modules plus requirements-cloud.txt, then test importing FreeCAD, Part, MeshPart and rendering a current bracket. Review and publish/republish the setup. A runnable environment must be verified after publication.

Suggested setup request:

> Prepare this AD5M hardware/CAD project for cloud work. Read README.md and AGENTS.md. Install a native FreeCAD runtime with working FreeCAD, Part and MeshPart Python imports; install requirements-cloud.txt into a compatible Python environment. Test the portable scripts/cad/ workflow on copies of outputs, preserving existing CAD and all historical revisions. Existing sketches/requirements call for rounded exterior edges, sharp hole rims allowed, support-free parts and specific mounting datums. Report any missing dependencies or sources. Do not claim physical fit from CAD. Publish only after the setup works.

## Current workstation prerequisites

Local GitHub sign-in was renewed successfully and a dry-run push passed on November 8, 2026. Cloud publication and successful remote upload are separate milestones. The in-app browser opened for cloud settings required a separate ChatGPT sign-in. Do not paste credentials into repository files or chat.

Official guide: https://learn.chatgpt.com/docs/environments/cloud-environments
