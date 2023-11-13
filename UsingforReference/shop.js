const Discord = require('discord.js');
const profileModel = require('../models/profileSchema')
//import {MessageActionRow, MessageButton, MessageEmbed} from 'discord.js'



module.exports = {
    name: 'shop',
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: 'Character shop only for display, no action happens here',
    async execute(client, message, args, Discord, profileData){

        function getRandomInt (min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        const backId = 'back'
        const forwardId = 'forward'
        const backButton = new Discord.MessageButton({
        style: 'SECONDARY',
//        label: 'Back',
        emoji: '⬅️',
        customId: backId
        })
        const forwardButton = new Discord.MessageButton({
        style: 'SECONDARY',
//        label: 'Forward',
        emoji: '➡️',
        customId: forwardId
        })

        const {author, channel} = message
        const char = ['char1', 'char2','char2', 'char3','char1', 'char2','char2', 'char3','char1', 'char2','char1', 'char2','char2', 'char3','char1', 'char2','char2', 'char3','char1', 'char2']


        const generateEmbed = async start => {
        const current = char.slice(start, start + 10) 

        // title: `Showing Characters ${start + 1}-${start + current.length} out of ${
        //    char.length}`
        return new Discord.MessageEmbed({
        title: `Character Shop`,
        description: 'Purchase Characters Here',
        fields: await Promise.all(
        current.map(async g => ({
        name: `${g}`,
        value: `Stamina: ${getRandomInt(50,100)} | Attack:  | Defense: | Mana: `
        }))
        )
        })
        }

    const canFitOnOnePage = char.length <= 10
    const embedMessage = await channel.send({
    embeds: [await generateEmbed(0)],
    components: canFitOnOnePage
    ? []
    : [new Discord.MessageActionRow({components: [forwardButton]})]
    })

    if (canFitOnOnePage) return

    const collector = embedMessage.createMessageComponentCollector({
    filter: ({user}) => user.id === author.id
    })

    let currentIndex = 0
    collector.on('collect', async interaction => {

    interaction.customId === backId ? (currentIndex -= 10) : (currentIndex += 10)

    await interaction.update({
    embeds: [await generateEmbed(currentIndex)],
    components: [
    new Discord.MessageActionRow({
        components: [

            ...(currentIndex ? [backButton] : []),

            ...(currentIndex + 10 < char.length ? [forwardButton] : [])
        ]
        })
    ]
    })
})        

    }

}

        // Character shop embed
        // const embed = new Discord.MessageEmbed()
        // .setColor('#FF0000')
        // .setTitle('Character Shop')
        // .setDescription('Purchase Characters Here')
        // .addFields(
        //     { name: 'Char 1', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        //     { name: 'Char 2', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        //     { name: 'Char 3', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        //     { name: 'Char 4', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        //     { name: 'Char 5', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        //     { name: 'Char 6', value: `Stamina:  | Attack:  | Defence: | Mana: `},
        // );

        // await message.channel.send({embeds: [embed] });

        // // .then(sentEmbed => {
        // //     sentEmbed.react("⬅️")
        // //     sentEmbed.react("➡️")
        // // });

        // client.on('messageReactionAdd', async (reaction, user) => {

        //     if(reaction.message.partial) await reaction.message.fetch();
        //     if(reaction.partial) await reaction.fetch();
        //     if(user.bot) return;
