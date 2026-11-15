import React from 'react';
import {Composition, Still} from 'remotion';
import {Main, TIMINGS, TAIL} from './Main';
import {Slide, HighYieldSlide} from './Slides';
const total = (k: string) => {
  const T = TIMINGS[k];
  return Math.ceil((T.starts[T.starts.length - 1] + T.durs[T.durs.length - 1]) * 30) + (k === 'student' ? TAIL : 0);
};
export const Root: React.FC = () => (
  <>
    <Composition id="Public" component={Main} durationInFrames={total('public')} fps={30} width={1080} height={1920}
      defaultProps={{cut: 'public' as const, bg: 'bg_public.mp4', audio: 'narration_public.wav', preview: false}} />
    <Composition id="Student" component={Main} durationInFrames={total('student')} fps={30} width={1080} height={1920}
      defaultProps={{cut: 'student' as const, bg: 'bg_student.mp4', audio: 'narration_student.wav', preview: false}} />
    <Still id="Slide" component={Slide} width={1080} height={1350} defaultProps={{deck: 'student' as const, idx: 0}} />
    <Still id="HighYield" component={HighYieldSlide} width={1080} height={1350} />
  </>
);
