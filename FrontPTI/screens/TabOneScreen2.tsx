import { SafeAreaView, Dimensions, ScrollView, Button, StyleSheet } from 'react-native';

// import EditScreenInfo from '../components/EditScreenInfo';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../types';
import { LineChart } from 'react-native-chart-kit';

const MyLineChart = () => {
  return (
    <>
      {/* <Text style={styles.header}>Line Chart</Text> */}
      <LineChart
        data={{
          labels: 
            ['January', 'February', 'March', 'April', 'May', 'June'],
          datasets: [
            {
              data: [20, 45, 28, 80, 99, 43],
              strokeWidth: 2,
            },
          ],
        }}
        width={Dimensions.get('window').width - 50}
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

export default function TabOneScreen2({ navigation }: RootTabScreenProps<'TabOne2'>) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Investment value historic</Text>
      <View>
        <MyLineChart />
      </View>
    <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      {/* <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" /> */}
      {/* <EditScreenInfo path="/screens/TabOneScreen.tsx" /> */}
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
