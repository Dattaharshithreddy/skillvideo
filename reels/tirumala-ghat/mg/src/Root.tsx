import React from 'react';
import {Composition, Still} from 'remotion';
import {Main} from './Main';
import {Cover} from './Cover';
import timing from './timing.json';
export const Root: React.FC = () => (
  <>
    <Composition id="Main" component={Main} durationInFrames={timing.end} fps={30} width={1080} height={1920}
      defaultProps={{bg: 'bg.mp4', audio: 'narration.wav', preview: false}} />
    <Still id="Cover" component={Cover} width={1080} height={1920} />
  </>
);
