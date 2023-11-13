const Discord = require('discord.js');
const profileModel = require('../models/profileSchema')

module.exports = {
    name: 'battle',
    aliases: [],
    permissions: [],
    cooldown: 5,
    description: 'battle',
    async execute(client, message, args, Discord, profileData){
        const randomNumber = Math.floor(Math.random() * 1000) + 1;
        const response = await profileModel.findOneAndUpdate(
            {
                userID: message.author.id,
            },
            {
                $inc: {
                coins: randomNumber,
                },
            }
            );
            message.channel.send(`You have recieved ${randomNumber}`);
        },
}
