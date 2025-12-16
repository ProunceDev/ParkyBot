import os, glob
from interactions import *

ext_filenames = glob.glob(os.path.join("Extensions", "**", "*.py"), recursive=True)
EXTENSIONS = [os.path.splitext(filename)[0].replace(os.path.sep, ".") for filename in ext_filenames]

QUESTIONS = [
    "Will you be able to attend the Juggernaut Event on <t:1766264400:F>?",
    "Do you accept the rules detailed in https://discord.com/channels/1082410307474968577/1333108418256310363 and understand that breaking them will result in instant death and a ban from the event?",
    "Have you read the entire post in the https://discord.com/channels/1082410307474968577/1333108418256310363?",
    "If applicable, will you be able to accept prize payment via PayPal only?",
    "Do you understand that if you cannot accept payment through PayPal, you may still participate but will forfeit any prize money if you win?",
    "Do you understand that all event players must watch Parky’s Twitch stream on the day of the event to follow along as it starts?",
    "Do you agree to use the Event Modpack, without adding any mods, to ensure fairness amongst all players as well as replay compatibility for the video?"
    "Can your PC and internet reliably run Minecraft without significant lag or crashes?",
    "Will you be a good sport if anything goes wrong during the event—whether on the player side or server side? (Issues happen often.)",
    "How old are you? (Not a dealbreaker.)",
    "Do you have a microphone? If so, do you agree to be respectful and polite to all players in the event so that Parky can use the footage in the video?",
    "Do you agree to capture a Flashback recording of your gameplay at the event so Parky can use your footage for the video? (tutorial provided to accepted members)",
    "Parky can gather any of your mic/gameplay after the event through your specific Flashback file. Do you agree to always keep your mic unmuted in order to generate good footage for the video?",
    "Will you accept in-game challenges or avoid them?",
    "What part of your personality, playstyle, or behavior do you think would stand out on camera?",
    "Why should we accept your application?"
]