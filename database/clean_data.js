conn = new Mongo();
db = conn.getDB("pokemon");

db.message_log.deleteMany({ server: "Hurricane HQ"});
db.message_log.deleteMany({ server: "Pokémon GO - Daytona Area"});
db.message_log.deleteMany({ channel: "mod-squad"});
db.message_log.deleteMany({ channel: "games-music"});
db.message_log.deleteMany({ server: "PoGO RVA"});


// db.message_log.aggregate([{$group: {_id: "$chanId",count: {$sum: 1}}}, {$limit: 500},{$sort: {count: -1}}])
// db.command_log.aggregate([{$group: {_id: "$server",count: {$sum: 1}}}, {$limit: 500},{$sort: {count: -1}}])

// db.message_log.aggregate([
//     {
//         $group: {
//             _id: {
//                 chandId: "$chanId",
//                 date: {
//                     'year': { '$year': "$verification_date" },
//                     'month': { '$month': "$verification_date" },
//                     'day': { '$dayOfMonth': "$verification_date" }
//                 },
//             },
//             count: {$sum: 1}
//         }
//     }, {
//         $limit: 500
//     }, {
//         $sort: {date: -1. count: -1}
//     }
// ])