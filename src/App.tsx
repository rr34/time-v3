import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div id='clock-area'>
        <img src='clock_images/timhouse20220410 - NL100550.PNG' className='clock-image' ></img>
        <svg width='3840' height='2160' viewBox='0 0 3840 2160' className='celestial-bodies'>
          <circle r="25" cx="2500" cy="500" fill="yellow" />
        </svg>
      </div>
    </>
  )
}

export default App
