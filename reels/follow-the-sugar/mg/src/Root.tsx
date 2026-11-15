import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import timing from './timing.json';
const total = Math.ceil((timing.starts[timing.starts.length - 1] + timing.durs[timing.durs.length - 1]) * 30);
export const Root: React.FC = () => (
  <>
    <Composition id="Main" component={Main} durationInFrames={total} fps={30} width={1080} height={1920}
      defaultProps={{bg: 'bg.mp4', audio: 'narration.wav', preview: false}} />
  </>
);
