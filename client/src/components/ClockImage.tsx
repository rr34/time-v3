function ClockImage() {
    const imageUrl = `${import.meta.env.VITE_FRONTEND_URL}/clock_images/timhouse20220410 - NL100541.PNG`;

    return (
        <img src={imageUrl} className='clock-image' alt="Clock" />
    );
}

export default ClockImage;
