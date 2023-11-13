const Discord = require('discord.js');
const charModel = require(`../models/CharSchema`);

module.exports = {
    name: 'addchar',
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: 'Adds a character to databse',
    async execute(client, message, args, Discord, profileData){
        function getRandomInt (min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }
    
        let charprofile = await charModel.create({   
            CharName: 'Billy',
            CharStamina: getRandomInt(60,100),
            CharAttack: getRandomInt(60,100),
            CharDefense: getRandomInt(60,100),
            CharMana: getRandomInt(60,100),
        })
        charprofile.save().then(console.log('Success'));
        }
}
