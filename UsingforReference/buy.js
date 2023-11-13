
module.exports = {
    name: "buy",
    aliases: ['purchase'],
    permissions: [],
    cooldown: 3,
    description: "Buy a character",
    execute(client, message, args, Discord, profileData){
        let character = args[0]
        switch(character)
        {
            case 'Sam':
                // do stuff
                break;
            case 'Matt':
                // stuff
                break;
            
            default:
                message.channel.send("You have either entered a wrong character or that character does not exist.")
        }
    }
}
