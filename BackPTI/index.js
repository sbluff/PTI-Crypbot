const config = require('./config')
const express = require('express')
const app = express()
const port = 8080

var cors = require('cors');
app.use(cors());

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

app.get('/mode', (req, res) => {
    connection.query("SELECT mode FROM bot_parameters;", function (err, result, fields) {
        if (err) throw err;
        res.send(result[0]['mode'].toString());
    });
});

app.get('/mode/update/:new_mode', (req, res) => {
    let new_mode = req.params.new_mode;
    let sql = "UPDATE bot_parameters SET mode ='" + new_mode +"';"
    connection.query(sql, function (err, result, fields) {
        if (err) throw err;
        res.send("Success");
    });
});

app.get('/credit', (req, res) => {
    connection.query("SELECT credit FROM bot_parameters;", function (err, result, fields) {
        if (err) throw err;
        res.send(result[0]['credit'].toString());
    });
});

app.get('/credit/update/:new_credit', (req, res) => {
    let new_credit = req.params.new_credit;
    let sql = "UPDATE bot_parameters SET credit =" + new_credit +";"
    connection.query(sql, function (err, result, fields) {
        if (err) throw err;
        res.send("Success");
    });
});

app.get('/packetSize', (req, res) => {
    connection.query("SELECT entryAmount as packetSize FROM bot_parameters;", function (err, result, fields) {
        if (err) throw err;
        res.send(result[0]['packetSize']);
    });
});

app.get('/packetSize/update/:new_credit', (req, res) => {
    let new_credit = req.params.new_credit;
    let sql = "UPDATE bot_parameters SET entryAmount ='" + new_credit +"';"
    connection.query(sql, function (err, result, fields) {
        if (err) throw err;
        res.send("Success");
    });
});

app.listen(port, () => {
  console.log(`PTI HTTP Server listening at http://localhost:${port}`)
})
