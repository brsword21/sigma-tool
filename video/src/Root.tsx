import {Composition} from 'remotion';
import {PickyDemo} from './PickyDemo';

export const RemotionRoot = () => (
  <Composition
    id="PickyDemo"
    component={PickyDemo}
    durationInFrames={1800}
    fps={30}
    width={1920}
    height={1080}
  />
);
