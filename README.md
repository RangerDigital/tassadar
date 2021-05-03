<p align="center">
  <h3 align="center">Tassadar</h3>
  <p align="center">Private Minecraft server playbooks and automation.</p>
</p>

---

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This repository contains the necessary **Ansible** playbooks, **Discord bot** source, and configuration needed to run my private on-demand **Minecraft server** for my friends.

But not running the server all the time I can significantly reduce costs to only **2€** per month running on **CPX11** instance.

<br>

## 🛠 How It Works

Friends of mine can request a server using a self-hosted Discord bot.

It then triggers GitHub Action workflow running Ansible playbook against Hetzner cloud.

Playbook rents a VPS, updates DNS entry for minecraft.bednarski.dev, configures Minecraft server with Nginx reverse proxy and custom monitoring endpoint.

For world persistence, I am using Hetzner block volume.

<br>

## 🚧 Contributing

**You are more than welcome to help me improve this project!**

Just fork this project from the `master` branch and submit a Pull Request (PR).

<br>

## 📃 License

This project is licensed under [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) .
