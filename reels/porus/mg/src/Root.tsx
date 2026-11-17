import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import timing from './timing.json';
export const Root: React.FC = () => (
  <Composition id="Reel" component={Reel} durationInFrames={timing.end} fps={30} width={1080} height={1920}
    defaultProps={{bg: 'bg.mp4', audio: 'narration.wav', music: 'music.wav', preview: false}} />
);
