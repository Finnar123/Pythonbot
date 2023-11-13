const profileModel = require("../models/profileSchema");

module.exports = {
    name: "gold",
    aliases: [],
    permissions: [],
    cooldown: 1,
    description: "Check your gold",
    async execute(client, message, args, Discord, profileData){
        let who;
        try{
            who = message.mentions.users.first().id;
        }catch{
        who = args[0];
        }
        
        if(who === undefined)
        {
            message.channel.send(`You have ${profileData.coins} gold.`)
        }else
        {
            
                if(!(who.match(/^[0-9]+$/)))
                {
                message.channel.send("Please enter it in this format: gold userid");
                return;
                }else if(who.length < 16)
                {
                    message.channel.send("I don't think thats a valid id.");
                    return;
                    // discord ids are generally 18 digits in length
                }

            let who2 = await profileModel.findOne({userID: who });
            message.channel.send("This user has " + who2.coins + " gold.");


        }
    }
}
