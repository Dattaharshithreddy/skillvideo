import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import timing from './timing.json';
export const Root: React.FC = () => (
  <Composition id="Main" component={Main} durationInFrames={timing.end} fps={30} width={1080} height={1920} />
);
