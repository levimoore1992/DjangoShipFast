# apps/misc/bot.py
import logging
import asyncio
import discord
from django.conf import settings

logger = logging.getLogger("main")


class DiscordClient:
    """
    A simplified Discord client for sending announcements to Discord channels.

    This client handles the complexity of Discord's async API by providing a
    synchronous interface that manages the event loop internally. It supports
    sending both plain text messages and rich embeds with various components.

    Attributes:
        token (str): The Discord bot token used for authentication.
    """

    def __init__(self, token=None):
        """
        Initialize the Discord client with a bot token.

        Args:
            token (str, optional): Discord bot token. If None, uses the token
                                  from Django settings.DISCORD_BOT_TOKEN.
        """
        self.token = token or settings.DISCORD_BOT_TOKEN

    def send_announcement(self, message=None, channel_id=None, embed=None):
        """
        Send an announcement to a Discord channel with optional rich embed.

        This is the main public method that provides a synchronous interface
        to Discord's asynchronous API. It handles creating an event loop and
        running the async operations in a controlled manner.

        Args:
            message (str, optional): Plain text message to send. Can be None if embed is provided.
            channel_id (str): The Discord channel ID to send the message to.
            embed (dict, optional): A dictionary containing embed configuration with the following
                                   possible keys:
                - title (str): The embed title
                - description (str): The embed description
                - color (int): The color of the embed's side bar (decimal value)
                - url (str): URL to make the title clickable
                - fields (list): List of field objects with 'name', 'value', and optional 'inline' keys
                - footer_text (str): Text to appear in the footer
                - thumbnail_url (str): URL to an image to display as thumbnail

        Returns:
            bool: True if message was sent successfully, False otherwise.

        Example:
            client = DiscordClient()
            client.send_announcement(
                message="Hello Discord!",
                channel_id="123456789012345678",
                embed={
                    'title': "Important Announcement",
                    'description': "This is a test announcement",
                    'color': 0x3498db,
                    'fields': [{'name': 'Field 1', 'value': 'Value 1', 'inline': True}]
                }
            )
        """
        # Validate required parameters
        if not channel_id:
            logger.error("No channel ID provided for Discord announcement")
            return False

        if not self.token:
            logger.error("Discord bot token not configured")
            return False

        # Create a new event loop for this operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async method and return its result
            return loop.run_until_complete(
                self._send_discord_message(message, channel_id, embed)
            )
        except Exception as e:
            # Catch any unexpected exceptions at the top level
            logger.error("Unexpected error in send_announcement: %s", str(e))
            return False
        finally:
            # Always ensure the loop is closed to prevent resource leaks
            loop.close()

    def validate_token(self):
        """
        Validate that the Discord bot token is properly configured.

        This method checks if the token is available and well-formed.

        Returns:
            bool: True if token appears valid, False otherwise
        """
        if not self.token:
            logger.warning("Discord bot token is not configured")
            return False

        # Basic validation that token has expected format
        if not isinstance(self.token, str) or len(self.token) < 50:
            logger.warning("Discord token appears to be malformed")
            return False

        return True

    async def _get_discord_channel(self, client, channel_id):
        """
        Retrieve a Discord channel by its ID.

        Args:
            client (discord.Client): The Discord client instance
            channel_id (str): ID of the channel to retrieve

        Returns:
            discord.Channel or None: The channel if found, None otherwise
        """
        try:
            # Try to get channel from cache first
            channel = client.get_channel(int(channel_id))
            if not channel:
                # If not in cache, try to fetch it
                channel = await client.fetch_channel(int(channel_id))

            if not channel:
                logger.error("Could not find Discord channel with ID: %s", channel_id)
                return None

            return channel

        except ValueError:
            # Handle case where channel_id is not a valid integer
            logger.error("Invalid Discord channel ID format: %s", channel_id)
        except discord.errors.NotFound:
            # Handle case where channel doesn't exist
            logger.error("Discord channel not found: %s", channel_id)
        except discord.errors.Forbidden:
            # Handle case where bot doesn't have access to the channel
            logger.error(
                "Bot doesn't have permission to access channel: %s", channel_id
            )
        except Exception as e:
            # Handle unexpected errors when getting channel
            logger.error("Error retrieving Discord channel %s: %s", channel_id, str(e))

        return None

    async def _create_discord_embed(self, embed_config):
        """
        Create a Discord embed object from configuration.

        Args:
            embed_config (dict): Embed configuration dictionary

        Returns:
            discord.Embed or None: The created embed or None if creation failed
        """
        if not embed_config:
            return None

        try:
            # Create the base embed object
            discord_embed = discord.Embed(
                title=embed_config.get("title"),
                description=embed_config.get("description"),
                color=embed_config.get("color"),
                url=embed_config.get("url"),
            )

            # Add fields if present
            if "fields" in embed_config and embed_config["fields"]:
                for field in embed_config["fields"]:
                    discord_embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False),
                    )

            # Add footer if present
            if "footer_text" in embed_config:
                discord_embed.set_footer(text=embed_config["footer_text"])

            # Add thumbnail if present
            if "thumbnail_url" in embed_config and embed_config["thumbnail_url"]:
                discord_embed.set_thumbnail(url=embed_config["thumbnail_url"])

            return discord_embed

        except Exception as e:
            # Handle errors in embed creation
            logger.error("Error creating Discord embed: %s", str(e))
            return None

    async def _send_discord_message(self, message, channel_id, embed_config):
        """
        Asynchronous helper method to send a message to Discord.

        This internal method handles the actual Discord API interaction using
        Discord.py's asynchronous interface. It manages the client lifecycle,
        channel retrieval, embed creation, and message sending.

        Args:
            message (str): Plain text message to send
            channel_id (str): Discord channel ID
            embed_config (dict): Embed configuration dictionary

        Returns:
            bool: True if successful, False otherwise

        Note:
            This method should not be called directly. Use send_announcement instead.
        """
        # Configure Discord client with appropriate intents
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        # Use a dictionary to store result across async contexts
        # This allows the on_ready event to communicate success/failure
        result = {"success": False}

        @client.event
        async def on_ready():
            """
            Event handler triggered when the Discord client is ready.
            """
            try:
                # Get the target channel
                channel = await self._get_discord_channel(client, channel_id)
                if not channel:
                    await client.close()
                    return

                # Create Discord embed object if configuration was provided
                discord_embed = await self._create_discord_embed(embed_config)

                # Send the message to the channel
                await channel.send(content=message, embed=discord_embed)
                logger.info(
                    "Successfully sent Discord announcement to channel %s", channel_id
                )
                result["success"] = True

            except Exception as e:
                # Handle any other errors during message sending
                logger.error("Error sending Discord message: %s", str(e))
            finally:
                # Always close the client when done to clean up resources
                await client.close()

        try:
            # Start the Discord client and wait for it to connect
            await client.start(self.token)
        except discord.errors.LoginFailure:
            # Handle invalid token
            logger.error("Failed to log in to Discord: Invalid token")
            return False
        except Exception as e:
            # Handle any other initialization errors
            logger.error("Failed to initialize Discord client: %s", str(e))
            return False

        # Return the success status from the on_ready handler
        return result["success"]


discord_bot = DiscordClient()
