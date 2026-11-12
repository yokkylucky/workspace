import {Composition} from 'remotion';
import {Demo} from './Demo';

export const RemotionRoot: React.FC = () => (
  <Composition id="Demo" component={Demo} durationInFrames={120} fps={30} width={1280} height={720} />
);
