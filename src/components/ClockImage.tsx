import imageAWIM from '../assets/clock_images/timhouse20220410 - NL100550.json';

function ClockImage() {
    console.log(imageAWIM['awim Angles Model xang_coeffs'])
    return (
        <img src='src/assets/clock_images/timhouse20220410 - NL100550.PNG' className='clock-image' ></img>
    );
}

export default ClockImage;