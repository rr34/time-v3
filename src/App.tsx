import { useEffect } from "react";
import ClockScreen from './components/ClockScreen';
import './App.css';

function App() {
  useEffect(() => {
      // POST request using fetch inside useEffect React hook
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'React Hooks POST Request Example' })
      };
      fetch('http://localhost:8000/testpost', requestOptions)
          .then(response => response.json())
          // .then(data => setPostId(data.id));
  
  // empty dependency array means this effect will only run once (like componentDidMount in classes)
  }, []);

  return (
    <div>
      <ClockScreen />
    </div>
  );
}

export default App
