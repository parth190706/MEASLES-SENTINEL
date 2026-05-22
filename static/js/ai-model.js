/**
 * ai-model.js — Teachable Machine model loader & predictor
 *
 * KEY FIX: Tensor memory leak on repeated predictions.
 * TF.js accumulates tensors each run. On the 2nd+ scan,
 * the backend stalls waiting for GPU/CPU memory that was never freed.
 * Solution: tf.tidy() wraps every prediction, disposing all intermediate
 * tensors automatically. Model itself is kept alive (not disposed).
 */

const MODEL_PATH = '/static/model/';
const LOAD_TIMEOUT_MS = 25000;

let model = null;
let modelLoading = false;
let modelLoadPromise = null;
let predictionCount = 0;

function waitForGlobal(name, timeoutMs = 12000) {
  return new Promise((resolve, reject) => {
    if (window[name]) { resolve(window[name]); return; }
    const start = Date.now();
    const interval = setInterval(() => {
      if (window[name]) {
        clearInterval(interval);
        resolve(window[name]);
      } else if (Date.now() - start > timeoutMs) {
        clearInterval(interval);
        reject(new Error(`Timed out waiting for "${name}" to load. Check your script tags.`));
      }
    }, 100);
  });
}

export async function loadModel() {
  if (model) return true;
  if (modelLoading && modelLoadPromise) return modelLoadPromise;

  modelLoading = true;
  modelLoadPromise = (async () => {
    try {
      await waitForGlobal('tf', 12000);
      const tm = await waitForGlobal('tmImage', 12000);

      // Warm up the TF.js backend before loading model
      await tf.ready();
      console.log('[AI] TF backend ready:', tf.getBackend());

      model = await Promise.race([
        tm.load(MODEL_PATH + 'model.json', MODEL_PATH + 'metadata.json'),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error(
            'Model load timed out (25s). Verify model.json, metadata.json and weights.bin exist in static/model/'
          )), LOAD_TIMEOUT_MS)
        )
      ]);

      console.log('[AI] Model loaded OK. Classes:', model.getTotalClasses(), '| TF tensors:', tf.memory().numTensors);
      return true;

    } catch (err) {
      modelLoading = false;
      modelLoadPromise = null;
      model = null;
      throw err;
    }
  })();

  return modelLoadPromise;
}

export async function predictImage(imgElement) {
  if (!model) throw new Error('Model not loaded. Call loadModel() first.');
  if (!imgElement || !imgElement.complete || imgElement.naturalWidth === 0) {
    throw new Error('Image is not ready. Wait for it to fully load before predicting.');
  }

  predictionCount++;
  const runId = predictionCount;
  console.log(`[AI] Prediction #${runId} starting. TF tensors before: ${tf.memory().numTensors}`);

  let rawPredictions;

  try {
    // tf.tidy() automatically disposes ALL intermediate tensors created inside it.
    // This is the core fix — without this, every predict() call leaks tensors
    // and TF.js stalls on the 2nd+ run.
    rawPredictions = await tf.tidy(() => {
      return model.predict(imgElement);
    });
  } catch (err) {
    // If prediction itself throws (e.g. backend in bad state), try resetting
    console.warn('[AI] Prediction error, attempting backend reset:', err.message);
    try {
      await tf.setBackend('cpu'); // fall back to CPU
      await tf.ready();
      rawPredictions = await tf.tidy(() => model.predict(imgElement));
    } catch (err2) {
      throw new Error('AI prediction failed even after reset: ' + err2.message);
    }
  }

  // Dispose any leftover tensors from previous runs every 3 predictions
  if (runId % 3 === 0) {
    tf.disposeVariables();
  }

  console.log(`[AI] Prediction #${runId} done. TF tensors after: ${tf.memory().numTensors}`);

  const results = rawPredictions
    .map(p => ({
      className: p.className,
      confidence: Math.round(p.probability * 100)
    }))
    .sort((a, b) => b.confidence - a.confidence);

  console.log('[AI] Results:', results);
  return results;
}

export function getRiskLevel({ className, confidence }) {
  const c = (className || '').toLowerCase();
  const conf = Number(confidence) || 0;

  if (c === 'normal') {
    return {
      level: 'low',
      label: 'Low Risk',
      advice: 'No rash indicators detected. Monitor symptoms and consult a doctor if concerned.'
    };
  }
  if (c === 'measles') {
    if (conf >= 70) return {
      level: 'high',
      label: 'High Risk — Measles Indicated',
      advice: 'Strong visual indicators of measles detected. Seek medical attention immediately.'
    };
    return {
      level: 'medium',
      label: 'Moderate Risk — Possible Measles',
      advice: 'Possible measles indicators. Consult a healthcare professional promptly.'
    };
  }
  if (c === 'monkeypox') {
    if (conf >= 70) return {
      level: 'high',
      label: 'High Risk — Monkeypox Indicated',
      advice: 'Strong visual indicators of monkeypox detected. Isolate and seek medical attention.'
    };
    return {
      level: 'medium',
      label: 'Moderate Risk — Possible Monkeypox',
      advice: 'Possible monkeypox indicators. Consult a healthcare professional promptly.'
    };
  }
  return {
    level: 'low',
    label: 'Low Risk',
    advice: 'No significant indicators detected. Consult a doctor if symptoms persist.'
  };
}

export function getGuidance(condition) {
  const c = (condition || '').toLowerCase();
  const shared = [
    'This is an AI screening result only — not a medical diagnosis.',
    'Consult a qualified healthcare professional for accurate diagnosis and treatment.',
    'Keep the affected area clean and avoid scratching.'
  ];
  if (c === 'measles') return [
    'Isolate yourself immediately — measles is highly contagious.',
    'Contact your doctor or nearest clinic right away.',
    'Do not go to school, work, or public places.',
    'Stay hydrated and rest.',
    'Avoid contact with pregnant women, infants, and immunocompromised individuals.',
    ...shared
  ];
  if (c === 'monkeypox') return [
    'Isolate yourself and avoid close contact with others.',
    'Cover all lesions with clean bandages to reduce spread.',
    'Contact your local health authority or doctor immediately.',
    'Do not share towels, bedding, or clothing.',
    'Wash hands frequently with soap and water.',
    ...shared
  ];
  return [
    'Your scan appears normal — monitor for any changes in the rash.',
    'If symptoms worsen or new symptoms appear, see a doctor.',
    'Maintain good hygiene and keep skin clean.',
    ...shared
  ];
}