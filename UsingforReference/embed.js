const Discord = require('discord.js');

module.exports = {
    name: 'embed',
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: 'Testing embed',
    execute(client, message, args){
        const embed = new Discord.MessageEmbed().setTitle('This is an embed.');

        message.channel.send({embeds: [embed] }).then(sentEmbed => {
            sentEmbed.react("1️⃣")
        });
    }
}