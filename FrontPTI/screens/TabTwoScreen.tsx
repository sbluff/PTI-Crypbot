import React, { Component } from 'react';
import { StyleSheet, TextInput, Button } from 'react-native';

// import EditScreenInfo from '../components/EditScreenInfo';
import { Text, View } from '../components/Themed';
import DropDownPicker from 'react-native-dropdown-picker';
import Multiselect from 'multiselect-react-dropdown';

export default function TabTwoScreen() {
  const [value3, onChangeText] = React.useState('  Insert amount');
  const [value4, onChangeText2] = React.useState('  Insert amount');

  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState(null);
  const [items, setItems] = React.useState([
    {label: '  Test', value: 'test'},
    {label: '  Production', value: 'prod'}
  ]);
  // const [open2, setOpen2] = React.useState(false);
  // const [value2, setValue2] = React.useState(null);
  // const [items2, setItems2] = React.useState([
  //   {label: '  Test', value: 'test', selectable: 'selectable'},
  //   {label: '  Production', value: 'prod', selectable: 'selectable'}
  // ]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Credit<br />
        <br />
      </Text>
      <TextInput
        style={{ height: 40, borderColor: 'gray', borderWidth: 1 }}
        onChangeText={text => onChangeText(text)}
        value={value3}
      />
      <Text style={styles.title}>
        <br />
        Packet size<br />
        <br />
      </Text>
      <TextInput
        style={{ height: 40, borderColor: 'gray', borderWidth: 1 }}
        onChangeText={text => onChangeText2(text)}
        value={value4}
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
        placeholder="  Select bot mode"
        showTickIcon={false}
        showArrowIcon={false}
      />
      <Text style={styles.title}>
        <br />
        Cryptos<br />
        <br />
      </Text>
      <Multiselect
        customCloseIcon={<>✖</>}
        options={[{name: 'ETH', id: 1}, {name: 'BTC', id: 2}, {name: 'SOL', id: 3}]}
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
      <Button
        // onPress={() => Alert.alert('Simple Button pressed')}
        title="Apply changes"
      />
      {/* <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      <EditScreenInfo path="/screens/TabTwoScreen.tsx" /> */}
    </View>
  );
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
