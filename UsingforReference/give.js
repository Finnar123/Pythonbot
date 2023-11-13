const profileModel = require('../models/profileSchema')

module.exports = {
    name: 'give',
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: 'give gold',
    async execute(client, message, args, Discord, profileData){

        let amountgiven = args[1];
        let receiverid;

        try{
            receiverid = message.mentions.users.first().id;
        }catch{
            console.log("No mention...looking for id.")
            receiverid = args[0];
            if(!(args[0].match(/^[0-9]+$/)))
            {
            message.channel.send("Please enter it in this format: command mention/id gold.");
            return;
            }else if(args[0].length < 16)
            {
                message.channel.send("I don't think thats a valid id.");
                return;
                // discord ids are generally 18 digits in length
            }

        }


        
        if(receiverid == message.author.id)
        {
            message.channel.send("You can't give yourself money!");
            return;
        }

        if(amountgiven > profileData.coins)
        {
            message.channel.send("You don't have enough gold to do that.");
            return;
        }

        if(amountgiven < 0)
        {
            message.channel.send("You can't give someone negative gold.");
            return;
        }
        
        const response = await profileModel.findOneAndUpdate(
                {
                    userID: message.author.id,
                },
                {
                    $inc: {
                    coins: -amountgiven,
                    },
                }
                );
        
        const response2 = await profileModel.findOneAndUpdate(
            {
                userID: receiverid,
            },
            {
                $inc: {
                coins: amountgiven,
                },
            }
            );
        message.channel.send("You have successfully given " + amountgiven + " gold.")
        
    }

}
