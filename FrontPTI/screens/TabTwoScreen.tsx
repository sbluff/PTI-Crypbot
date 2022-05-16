import React, { Component } from 'react';
import { StyleSheet, TextInput, Button, Alert } from 'react-native';

// import EditScreenInfo from '../components/EditScreenInfo';
import { Text, View } from '../components/Themed';
import DropDownPicker from 'react-native-dropdown-picker';
import Multiselect from 'multiselect-react-dropdown';
import axios from 'axios';

let credit = "  Insert amount";
getCredit();

let PSize = "  Insert amount";
getPSize();

let mode = "test";
getMode();

export default function TabTwoScreen() {

  const [value3, onChangeText] = React.useState(credit);
  const [value4, onChangeText2] = React.useState(PSize);

  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState(mode);
  const [items, setItems] = React.useState([
    {label: '  Test', value: 'test'},
    {label: '  Production', value: 'prod'}
  ]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Credit<br />
        <br />
      </Text>
      <TextInput
        style={{ width: 185, height: 40, borderColor: 'gray', borderWidth: 1 }}
        onChangeText={text => cr(text)}
        onChange={text => onChangeText(text)}
        value={credit}
      />
      <Text style={styles.title}>
        <br />
        Packet size<br />
        <br />
      </Text>
      <TextInput
        style={{ width: 185, height: 40, borderColor: 'gray', borderWidth: 1 }}
        onChangeText={text => ps(text)}
        onChange={text => onChangeText2(text)}
        value={PSize}
      />
      <Text style={styles.title}>
        <br />
        Bot mode<br />
        <br />
      </Text>
      <DropDownPicker
        style={{ width: 185, height: 40, borderColor: 'gray', borderWidth: 0.5, alignSelf: 'center'}}
        containerStyle={{ width: 185, height: 40, borderColor: 'gray', borderWidth: 1, alignSelf: 'center'}}
        textStyle={{ marginVertical: 10}}
        open={open}
        value={value}
        items={items}
        setOpen={setOpen}
        setValue={setValue}
        setItems={setItems}
        placeholder=" "
        showTickIcon={false}
        showArrowIcon={false}
        onChangeValue={(mode) => mo(mode)}
      />
      <Text style={styles.title}>
        <br />
        Cryptos<br />
        <br />
      </Text>
      <Multiselect
        customCloseIcon={<>✖</>}
        selectedValues={[{name: 'BTC', id: 2}]}
        options={[{name: 'ETH', id: 1}, {name: 'BTC', id: 2}, {name: 'SOL', id: 3}, {name: 'ADA', id: 4}]}
        style= {{
          searchBox: {
            borderColor: 'grey',
            'border-radius': '0px',
            width: 185,
            height: 40,
            color: 'green',
          },
          chips: {
            background: 'white',
            border: '1px solid #5094d3',
            color: 'black',
          },
        }}
        // selectedValues={this.state.selectedValue}
        // onSelect={this.onSelect}
        // onRemove={this.onRemove}
        displayValue="name"
        placeholder="Select cryptos"
      />
      <Text style={styles.title}>
        <br />
        <br />
      </Text>
      <View style={{ flexDirection:"row" }}>
        <View style={{ width: 150, marginRight: 20 }}>
          <Button
            //onPress={() => alert('Changes applied succesfully')}
            onPress={() => applychanges()}
            title="Apply changes"
          />
        </View>
        <View style={{ width: 150, marginLeft: 20 }}>
          <Button
            onPress={() => clearval1()}
            title="Clear values"
          />
        </View>
      </View>
      {/* <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      <EditScreenInfo path="/screens/TabTwoScreen.tsx" /> */}
    </View>
  );
}

function clearval1(){
  alert('Values cleared');
  clearValues();
}

function clearValues(){
  axios.get('http://localhost:8080/trades/delete')
  .then((response) => {
    console.log("succes")
  })
} 

function applychanges(){
  alert('Changes applied succesfully');
  setCredit();
  setPSize();
  setMode();
}

function cr(txt){
  credit = txt;
  console.log(txt);
}

function ps(txt){
  PSize = txt;
  console.log(txt);
}

function mo(txt){
  mode = txt;
  console.log(txt);
}

function getCredit(){
  axios.get('http://localhost:8080/credit')
  .then(response => {
    console.log(response.data)
    credit = "  "+response.data
  })

  //return "hola";
}

function setCredit(){
  axios.get('http://localhost:8080/credit/update/'+credit)
  .then(response => {
    console.log(response.data)
    console.log(credit)
  })

  //return "hola";
}

function getPSize(){
  axios.get('http://localhost:8080/packetSize')
  .then(response => {
    console.log(response.data)
    PSize = "  "+response.data
  })

  //return "hola";
}

function setPSize(){
  axios.get('http://localhost:8080/packetSize/update/'+PSize)
  .then(response => {
    console.log(response.data)
    console.log(PSize)
  })

  //return "hola";
}

function getMode(){
  axios.get('http://localhost:8080/mode')
  .then(response => {
    console.log(response.data)
    mode = response.data
  })

  //return "hola";
}

function setMode(){
  axios.get('http://localhost:8080/mode/update/'+mode)
  .then(response => {
    //console.log(response.data)
    console.log(mode)
  })

  //return "hola";
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
});
