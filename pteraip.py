import discord
import requests
from discord.ext import commands
from discord import app_commands, Embed
from discord.app_commands import Choice
import json

from pydactyl import PterodactylClient


class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        with open("config.json", "r") as f:
            self.config = json.load(f)

        self.ptapi = PterodactylClient(url=f"{self.config['host']}",
                                       api_key=f"{self.config['api_key']}")

    @app_commands.command(
        name="config",
        description="Configuring the configuration file"
    )
    @app_commands.describe(
        name="Name",
        value="Value"
    )
    @app_commands.choices(
        name=[
            Choice(name="API Key", value="api_key"),
            Choice(name="URL Hosting panel", value="host"),
            Choice(name="Server ID", value="server_id"),
            Choice(name="Trust role ID", value="trust_role_id")
        ]
    )
    async def conf(self, interaction: discord.Interaction, name: str, value: str):
        pass

    # coming soon

    @app_commands.command(name="stats", description="Інформація стосовно серверу Minecraft")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Waiting response for {self.config['host']}")
        server = self.ptapi.client.servers.get_server(server_id=self.config["server_id"])
        s_utilis = self.ptapi.client.servers.get_server_utilization(server_id=self.config["server_id"])

        embed = Embed(title="Server information",
                      description="""
The bot cannot always receive information from the server for various reasons,
it's basically a hosting problem.
You can check it here: https://status.sneakyhub.com/
""")
        embed.add_field(name="Server state", value="{0}".format(s_utilis["current_state"]))
        embed.add_field(name="Server IP", value="{0}".format(str(server["relationships"]
                                                                 ["allocations"]["data"]
                                                                 [0]["attributes"]
                                                                 ["ip_alias"]) + ":" + str(server["relationships"]
                                                                                           ["allocations"]["data"]
                                                                                           [0]["attributes"]
                                                                                           ["port"])))
        embed.add_field(name="Node", value="{0}".format(server["node"]))
        await interaction.edit_original_response(content="", embed=embed)

    @app_commands.command(
        name="power",
        description="Enable, reload or disable server"
    )
    @app_commands.describe(
        action="Action"
    )
    @app_commands.choices(
        action=[
            Choice(name="Enable server", value="enable"),
            Choice(name="Disable server(Need perms)", value="disable"),
            Choice(name="Realod(Need perms)", value="reboot")
        ]
    )
    async def power(self, interaction: discord.Interaction, action: str = "enable"):
        await interaction.response.send_message(f"Waiting response for {self.config['host']}")
        list_roles = []
        for roles in interaction.user.roles:
            list_roles.append(roles.id)
        if action == "enable":

            self.ptapi.client.servers.send_power_action(server_id=self.config["server_id"], signal="start")
            await interaction.edit_original_response(content="The command has been sent. Let's turn on the server!")

        elif action == "disable":
            if not self.config["trust_role_id"] in list_roles:
                await interaction.edit_original_response(content="Insufficient rights to use the parameter")
            else:
                self.ptapi.client.servers.send_power_action(server_id=self.config["server_id"], signal="stop")
                await interaction.edit_original_response(content="The command has been sent. Shutdown server:(")

        elif action == "reboot":
            if not self.config["trust_role_id"] in list_roles:
                await interaction.edit_original_response(content="Insufficient rights to use the parameter")
            else:
                self.ptapi.client.servers.send_power_action(server_id=self.config["server_id"], signal="restart")
                await interaction.edit_original_response(content="The command has been sent. Reloading...")

    @app_commands.command(
        name="send",
        description="Send command to server"
    )
    @app_commands.describe(
        command = "Your command"
    )
    async def cmd(self, interaction: discord.Interaction, command: str):
        await interaction.response.send_message(f"Waiting response for {self.config['host']}")
        try:
            self.ptapi.client.servers.send_console_command(server_id=self.config["server_id"], cmd=command)
            await interaction.edit_original_response(content="Command sended!")
        except requests.HTTPError:
            await interaction.edit_original_response(content="failed.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Main(bot))
