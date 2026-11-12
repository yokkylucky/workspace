import {Composition} from 'remotion';
import {Demo} from './Demo';
import {LalaMarche} from './lalamarche/LalaMarche';
import timeline from './lalamarche/timeline.json';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Demo" component={Demo} durationInFrames={120} fps={30} width={1280} height={720} />
    <Composition id="LalaMarcheNarration" component={LalaMarche} defaultProps={{narration: true}}
      durationInFrames={timeline.total} fps={30} width={1080} height={1920} />
    <Composition id="LalaMarcheSilent" component={LalaMarche} defaultProps={{narration: false}}
      durationInFrames={timeline.total} fps={30} width={1080} height={1920} />
  </>
);
