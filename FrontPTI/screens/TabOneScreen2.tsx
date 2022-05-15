import { SafeAreaView, Dimensions, ScrollView, Button, StyleSheet } from 'react-native';

// import EditScreenInfo from '../components/EditScreenInfo';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../types';
import { LineChart } from 'react-native-chart-kit';
import axios from 'axios'
// // import {tableData} from '../data/tableData';

// console.log("HELLOOOOO: ")
// console.log(tableData)

let coins_transactions = []
let tradesData:number[] = []
// let tradesLabel:string[] = []
setTradesData()

const MyLineChart = () => {
  return (
    <>
      {/* <Text style={styles.header}>Line Chart</Text> */}
      <LineChart
        data={{
          labels: 
            [],
          datasets: [
            {
              data: tradesData,
              strokeWidth: 3,
            },
          ],
        }}
        width={Dimensions.get('window').width - 50}
        yAxisSuffix="BTC"
        height={Dimensions.get('window').height - 600}
        chartConfig={{
          backgroundColor: '#1cc910',
          
          backgroundGradientFrom: '#eff3ff',
          backgroundGradientTo: '#efefef',
          decimalPlaces: 2,
          color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
          style: {
            borderRadius: 16,
            marginHorizontal: 50,
          },
        }}
        style={{
          marginVertical: 8,
          borderRadius: 16,
        }}
      />
    </>
  );
};

export default function TabOneScreen({ navigation }: RootTabScreenProps<'TabOne'>) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>BTC Tokens</Text>
      <View>
        <MyLineChart />
      </View>
    <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      {/* <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" /> */}
      {/* <EditScreenInfo path="/screens/TabOneScreen.tsx" /> */}
    </View>
  );
}

//updates tradesData value and tradesLabels
function setTradesData(){
  let coins_amount = 0
  axios.get('http://localhost:8080/trades')
  .then((response) => {
    let trades = response.data
    for(let i:number = 0; i < response.data.length; i++){
      coins_amount += trades[i]['number_coins']
      coins_transactions.push({"coins_balance": coins_amount, "date": trades[i]['startDate']})
    }
  })

  axios.get('http://localhost:8080/trades/close')
  .then((response) => {
    let trades = response.data
    for(let i:number = 0; i < response.data.length; i++){
      coins_amount += trades[i]['number_coins']*-1
      coins_transactions.push({"coins_balance": coins_amount, "date": trades[i]['closeDate']})
    }
    coins_transactions.sort(function(a,b){
      let dateA = new Date(a['date']).getTime()
      let dateB = new Date(b['date']).getTime()
      return dateA - dateB
    })

    console.log(coins_transactions)
    for(let i:number = 0; i < coins_transactions.length; i++){
      tradesData.push(coins_transactions[i]['coins_balance'])
    }
  })
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
    marginVertical: 50,
    marginHorizontal: 50,
  },
  separator: {
    marginBottom: 50,
    marginTop: 100,
    marginHorizontal: 50,
    height: 1,
    width: '80%',
  },
});
