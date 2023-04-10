import React, {useState, useEffect} from 'react'


function App() {
    const [data, setData] = useState([{}])

    useEffect(() => {
        fetch("/time").then (
            res => res.json()
        ).then (
            data => {
                setData(data)
                console.log(data)
            }
        )
    }, [])

    return (
        <div>
            {(typeof data.timeseries === "undefined") ? (
                <p>Loading...</p>
            ) : (
                data.timeseries.map((item, i) => (
                    <p key={i}>{item}</p>
                ))
            )}
        </div>
    )
}


export default App;