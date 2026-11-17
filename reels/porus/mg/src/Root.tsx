import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {Sample, SHOT_LEN} from './Sample';
import timing from './timing.json';
export const Root: React.FC = () => (<>
  <Composition id="Sample" component={Sample} durationInFrames={SHOT_LEN * 3} fps={30} width={1080} height={1920} />
  <Composition id="Main" component={Main} durationInFrames={timing.end} fps={30} width={1080} height={1920}
    defaultProps={{bg: 'bg.mp4', audio: 'narration.wav', preview: false}} />

</>);
