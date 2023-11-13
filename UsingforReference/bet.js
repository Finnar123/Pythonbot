const profileModel = require('../models/profileSchema')

module.exports = {
    name: 'bet',
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: 'bet gold',
    async execute(client, message, args, Discord, profileData){
        const randomNumber = Math.floor(Math.random() * 2);
        let betlimit = 10000000;
        let amountbet = args[0];
        if(amountbet % 1 != 0 || amountbet <= 0)
        {
            message.channel.send("Please enter a valid number.");
            return;
        }
        if(amountbet > betlimit)
        {
            message.channel.send("You are betting too much! The maximum bet allowed is " + betlimit + ".");
            return;
        }

        if(amountbet > profileData.coins)
        {
            message.channel.send("You don't have enough gold to do that bet!");
            return;
        }

        if(randomNumber == 0)
        {
            message.channel.send("You have lost the bet! You lose " + amountbet + " gold.")
            const response = await profileModel.findOneAndUpdate(
                {
                    userID: message.author.id,
                },
                {
                    $inc: {
                    coins: -amountbet,
                    },
                }
                );
        }else
        {
        const response2 = await profileModel.findOneAndUpdate(
            {
                userID: message.author.id,
            },
            {
                $inc: {
                coins: amountbet,
                },
            }
            );
            message.channel.send(`You won the bet! You have recieved ${amountbet}`);
        }
    }

}
