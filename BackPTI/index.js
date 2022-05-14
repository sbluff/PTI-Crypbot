const config = require('./config')
const express = require('express')
const app = express()
const port = 8080

var mysql      = require('mysql');
var connection = mysql.createConnection({
  host     : config['db']['host'],
  user     : config['db']['user'],
  password : config['db']['password'],
  database : config['db']['database']
});

// connection.connect();
connection.connect(function(err) {
    if (err) throw err;
});

//all trades
app.get('/trades', (req, res) => {
    // let res;
    connection.query("SELECT * FROM trades", function (err, result, fields) {
        if (err) throw err;
        res.send(result);
    });
})

//opened trades
app.get('/trades/open', (req, res) => {
    // let res;
    connection.query("SELECT * FROM trades WHERE status='opened';", function (err, result, fields) {
        if (err) throw err;
        res.send(result);
    });
})

//closed trades
app.get('/trades/close', (req, res) => {
    // let res;
    connection.query("SELECT * FROM trades WHERE status='closed';", function (err, result, fields) {
        if (err) throw err;
        res.send(result);
    });
})

app.listen(port, () => {
  console.log(`PTI HTTP Server listening at http://localhost:${port}`)
})
