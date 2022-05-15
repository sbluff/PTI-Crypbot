const options = {
    method: 'POST',
    headers: myHeaders,
    body: new URLSearchParams({
      'user': user,
      'password': password,
      'session': session
    }),
}

export const tableData = new Request('http://localhost:3000/valCreden/', options);
// export let tableData = async () => {
//     await (await fetch('localhost:8080/trades')).json();
// }

// fetch('http://localhost:8080/trades')
//     .then(res => res.json())
//     .then(json => {
//         console.log("HELLO THERE");
//         console.table(json);
// })