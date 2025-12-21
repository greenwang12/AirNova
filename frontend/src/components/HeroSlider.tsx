import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import plane from "../assets/images/airplane.png";
import gif1 from "../assets/gifs/airport1.gif";
import gif2 from "../assets/gifs/airport2.gif";

const slides = [plane, gif1, gif2];

export default function HeroSlider() {
  return (
    <Slider
      className="hero"
      dots
      infinite
      autoplay
      speed={800}
      fade
      arrows
    >
      {slides.map((src, i) => (
        <img key={i} src={src} alt="" />
      ))}
    </Slider>
  );
}
