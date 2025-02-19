import { useState } from "react";
import { useEffect } from "react";
import ClockScreen from './components/ClockScreen';
import './App.css';

function App() {
  const [PostId, setPostId] = useState(11111)
  useEffect(() => {
      // POST request using fetch inside useEffect React hook
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ requestType: 'get time strings', moments: ['2025-02-19T11:19Z', '2025-02-19T11:20Z']})
      };
      fetch('http://localhost:8000/testpost', requestOptions)
          .then(response => console.log(response.json()))
          .then(data => console.log(data["id"]));
  // empty dependency array means this effect will only run once (like componentDidMount in classes)
  }, []);

  return (
    <div>
      {/* <ClockScreen /> */}
      <p>{PostId}</p>
    </div>
  );
}

export default App
