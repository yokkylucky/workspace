import {Config} from '@remotion/cli/config';
// プリインストール済みのChromiumを使う（GPUなし環境ではANGLE/SwiftShaderでWebGLを描画）
Config.setBrowserExecutable(process.env.REMOTION_CHROME ?? null);
Config.setChromiumOpenGlRenderer('swangle');
