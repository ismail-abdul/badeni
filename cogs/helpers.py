from services.queueNode import QueueNode
from nextcord import Interaction

def streamEndsOrError(self, interaction: Interaction):
        """
        Using a higher order function provides context to func without breaking the defintion for after.
        Once called, this lower func with 'hidden' context is returned. 
        Hence, we have an finalizer function/coroutine with only error. In theory, 
        we could apply args and kwargs to this pattern.
        """
        async def func(error: Exception | None):
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=False, with_message=True)
            vc: VoiceClient = interaction.guild.voice_client # type: ignore
    
            # i.e. connection loss, player fails to process audio, server fails etc. Need to handle each case seperately later.
            if error:
                if vc.is_playing():
                    vc.pause()
                await vc.disconnect()
                self.queue.clear()
                await interaction.send("Error whilst playing (queue cleared). Disconnecting voice client.")
                print(error)
                return 
            
            if self.queue.isEmpty:
                if vc.is_playing():
                    vc.pause()
                await vc.disconnect()
                await interaction.send("Stream ended. Disconnecting voice client.")
                return
            
            node: QueueNode = self.queue.dequeue()
            if vc.is_playing():
                vc.stop()
            vc.play(source=node.source, after = self.streamEndsOrError(interaction))
            await interaction.send('Playing the next song.') # Improve UX here. Need to make some cool embeds. Mb some templating can be created.
        
        return func