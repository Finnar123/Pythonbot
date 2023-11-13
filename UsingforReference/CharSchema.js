const mongoose = require('mongoose');

const charSchema = new mongoose.Schema({
    usercharID: {type: String, unique: true},
    cardID: {type: String, unique: true},
    CharName: {type: String, require: true},
    CharStamina: {type: Number, default: 0},
    CharAttack: {type: Number, default: 0},
    CharDefense: {type: Number, default: 0},
    CharMana: {type: Number, default: 0},

})

const model = mongoose.model('CharacterModels', charSchema);

module.exports = model;