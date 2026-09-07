import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

const LINE_INFO = {
  life: {
    label: 'Life Line',
    icon: '🌱',
  },
  head: {
    label: 'Head Line',
    icon: '🧠',
  },
  heart: {
    label: 'Heart Line',
    icon: '❤️',
  },
  fate: {
    label: 'Fate Line',
    icon: '⭐',
  },
  sun: {
    label: 'Sun Line',
    icon: '☀️',
  },
}

const LINE_ORDER = [
  'life',
  'head',
  'heart',
  'fate',
  'sun',
]

export default function PalmReading() {
  const { token } = useAuth()

  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview)
      }
    }
  }, [preview])

  function handleFileChange(e) {
    const selected = e.target.files?.[0]

    if (!selected) {
      return
    }

    if (!selected.type.startsWith('image/')) {
      setError('Please select a valid image.')
      return
    }

    if (selected.size > 10 * 1024 * 1024) {
      setError('Image must be 10 MB or smaller.')
      return
    }

    if (preview) {
      URL.revokeObjectURL(preview)
    }

    setFile(selected)
    setPreview(URL.createObjectURL(selected))
    setResult(null)
    setError(null)
  }

  async function handleAnalyze() {
    if (!file) {
      setError('Please select a palm image first.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('image', file)

    try {
      const response = await fetch(
        '/api/palm/analyze',
        {
          method: 'POST',
          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {},
          body: formData,
        }
      )

      let data

      try {
        data = await response.json()
      } catch {
        throw new Error(
          'The server returned an invalid response.'
        )
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
            `Analysis failed with status ${response.status}.`
        )
      }

      setResult(data)
    } catch (err) {
      console.error('Palm analysis error:', err)

      setError(
        err.message ||
          'Could not reach the palm analysis service. Make sure the backend is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  function resetAnalysis() {
    if (preview) {
      URL.revokeObjectURL(preview)
    }

    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-10">

      {/* ===================================================== */}
      {/* PAGE HEADER */}
      {/* ===================================================== */}

      <section className="text-center">

        <p className="uppercase tracking-[0.3em] text-lavender text-xs mb-3">
          AI Palm Analysis
        </p>

        <h1 className="font-display text-5xl md:text-6xl text-parchment mb-4">
          Discover Your Palm
        </h1>

        <p className="text-parchment/60 max-w-2xl mx-auto">
          Upload a clear image of your open palm. The computer-vision
          model will identify visible palm lines and provide an
          entertainment-style interpretation.
        </p>

      </section>


      {/* ===================================================== */}
      {/* UPLOAD + ORIGINAL IMAGE */}
      {/* ===================================================== */}

      <section className="grid md:grid-cols-2 gap-8">

        <div className="card">

          <h2 className="font-display text-2xl text-gold mb-2">
            Upload Your Palm
          </h2>

          <p className="text-sm text-parchment/50 mb-5">
            Use a clear, well-lit photo with your entire palm visible.
          </p>

          <label
            htmlFor="palm-upload"
            className="block border-2 border-dashed border-lavender/30 rounded-xl
                       min-h-[320px] flex items-center justify-center
                       cursor-pointer hover:border-gold/60 transition-colors
                       overflow-hidden bg-midnight/30"
          >

            {preview ? (
              <img
                src={preview}
                alt="Uploaded palm"
                className="h-full w-full min-h-[320px] object-contain"
              />
            ) : (
              <div className="text-center px-6">

                <div className="text-5xl mb-4">
                  ✋
                </div>

                <p className="text-parchment/70 text-sm">
                  Click here to choose your palm image
                </p>

                <p className="text-parchment/40 text-xs mt-2">
                  JPEG, PNG or WebP • Maximum 10 MB
                </p>

              </div>
            )}

          </label>

          <input
            id="palm-upload"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="flex gap-3 mt-6">

            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="btn-primary flex-1"
            >
              {loading
                ? 'Analyzing Palm…'
                : 'Analyze Palm'}
            </button>

            {(file || result) && (
              <button
                onClick={resetAnalysis}
                disabled={loading}
                className="btn-secondary"
              >
                Reset
              </button>
            )}

          </div>

          {loading && (
            <div className="mt-5">

              <div className="h-2 bg-midnight rounded-full overflow-hidden">

                <div
                  className="h-full bg-gold animate-pulse"
                  style={{ width: '70%' }}
                />

              </div>

              <p className="text-xs text-parchment/50 mt-2 text-center">
                Detecting palm lines and generating your reading…
              </p>

            </div>
          )}

          {error && (
            <div className="mt-5 p-4 rounded-xl border border-red-400/30 bg-red-950/20">
              <p className="text-red-300 text-sm">
                {error}
              </p>
            </div>
          )}

        </div>


        {/* ================================================= */}
        {/* QUICK INFORMATION */}
        {/* ================================================= */}

        <div className="card">

          <h2 className="font-display text-2xl text-gold mb-5">
            What We Analyze
          </h2>

          <div className="space-y-4">

            {LINE_ORDER.map((line) => {

              const info = LINE_INFO[line]

              return (
                <div
                  key={line}
                  className="flex items-center gap-4
                             border-b border-lavender/10 pb-4"
                >

                  <div className="text-2xl">
                    {info.icon}
                  </div>

                  <div>
                    <h3 className="text-parchment font-medium">
                      {info.label}
                    </h3>

                    <p className="text-xs text-parchment/40 mt-1">
                      AI visual detection
                    </p>
                  </div>

                </div>
              )
            })}

          </div>

          <div className="mt-6 p-4 rounded-xl bg-gold/5 border border-gold/10">

            <p className="text-xs text-parchment/50 leading-relaxed">
              Palm-line locations are detected from the uploaded image.
              Traditional palmistry interpretations are provided for
              entertainment and self-reflection and are not scientifically
              validated predictions.
            </p>

          </div>

        </div>

      </section>


      {/* ===================================================== */}
      {/* RESULTS */}
      {/* ===================================================== */}

      {result && (
        <PalmResults result={result} />
      )}

    </div>
  )
}


/* ========================================================= */
/* RESULTS COMPONENT */
/* ========================================================= */

function PalmResults({ result }) {

  const annotatedImage =
    result.annotated_image
      ? `data:image/jpeg;base64,${result.annotated_image}`
      : null

  return (
    <div className="space-y-8">

      {/* =================================================== */}
      {/* RESULT HEADER */}
      {/* =================================================== */}

      <section className="text-center">

        <p className="uppercase tracking-[0.3em] text-lavender text-xs mb-2">
          Analysis Complete
        </p>

        <h2 className="font-display text-4xl text-gold">
          Your Palm Reading
        </h2>

      </section>


      {/* =================================================== */}
      {/* ANNOTATED IMAGE */}
      {/* =================================================== */}

      <section className="card">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">

          <div>
            <h3 className="font-display text-2xl text-gold">
              Detected Palm Lines
            </h3>

            <p className="text-xs text-parchment/40 mt-1">
              Green boxes show regions detected by the YOLO model.
            </p>
          </div>

          <div className="text-sm text-parchment/60">

            Overall confidence:{' '}

            <span className="text-gold font-semibold">
              {Math.round(
                (result.confidence || 0) * 100
              )}
              %
            </span>

          </div>

        </div>


        {annotatedImage ? (

          <div className="rounded-2xl overflow-hidden border border-lavender/20 bg-midnight">

            <img
              src={annotatedImage}
              alt="AI annotated palm showing detected lines"
              className="w-full max-h-[750px] object-contain mx-auto"
            />

          </div>

        ) : (

          <div className="rounded-xl border border-lavender/20 p-10 text-center">

            <p className="text-parchment/50 text-sm">
              The annotated image was not returned by the backend.
            </p>

            <p className="text-parchment/30 text-xs mt-2">
              Check that palm_line_detector.py returns annotated_image.
            </p>

          </div>

        )}

      </section>


      {/* =================================================== */}
      {/* DETECTION CARDS */}
      {/* =================================================== */}

      <section className="card">

        <h3 className="font-display text-2xl text-gold mb-5">
          Detected Features
        </h3>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">

          {LINE_ORDER.map((line) => {

            const info = LINE_INFO[line]

            const analysis =
              result.line_analysis?.[line]

            const detection =
              findDetection(
                result.detections,
                line
              )

            const detected =
              analysis?.detected ??
              !!detection

            const confidence =
              analysis?.confidence ??
              detection?.confidence ??
              0

            return (

              <div
                key={line}
                className={
                  detected
                    ? 'rounded-xl border border-green-400/30 bg-green-950/10 p-5'
                    : 'rounded-xl border border-lavender/15 bg-midnight/20 p-5 opacity-70'
                }
              >

                <div className="flex items-center justify-between gap-2">

                  <div className="flex items-center gap-2">

                    <span className="text-xl">
                      {info.icon}
                    </span>

                    <h4 className="font-medium">
                      {info.label}
                    </h4>

                  </div>

                  {detected ? (
                    <span className="text-xs text-green-300">
                      Detected
                    </span>
                  ) : (
                    <span className="text-xs text-parchment/40">
                      Not found
                    </span>
                  )}

                </div>


                <div className="mt-4">

                  <div className="flex justify-between text-xs mb-1">

                    <span className="text-parchment/50">
                      Confidence
                    </span>

                    <span className="text-gold">
                      {Math.round(
                        confidence * 100
                      )}
                      %
                    </span>

                  </div>

                  <div className="h-1.5 bg-midnight rounded-full overflow-hidden">

                    <div
                      className="h-full bg-gold transition-all"
                      style={{
                        width: `${Math.min(
                          confidence * 100,
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>


                <p className="text-xs text-parchment/50 leading-relaxed mt-4">

                  {analysis?.interpretation ||
                    result.insights?.[
                      `${line}_line`
                    ] ||
                    `${info.label} was not clearly detected in this image.`}

                </p>

              </div>

            )
          })}

        </div>

      </section>


      {/* =================================================== */}
      {/* PALM SHAPE + FINGER STRUCTURE */}
      {/* =================================================== */}

      <section className="grid md:grid-cols-2 gap-8">

        <PalmShapeCard
          palmShape={result.palm_shape}
        />

        <FingerStructureCard
          fingerStructure={
            result.finger_structure
          }
        />

      </section>


      {/* =================================================== */}
      {/* GENERAL INTERPRETATION */}
      {/* =================================================== */}

      {result.interpretation && (
        <InsightReport
          interpretation={
            result.interpretation
          }
        />
      )}

    </div>
  )
}


/* ========================================================= */
/* PALM SHAPE */
/* ========================================================= */

function PalmShapeCard({ palmShape }) {

  if (!palmShape) {
    return (
      <section className="card">
        <h3 className="font-display text-2xl text-gold mb-3">
          Palm Shape
        </h3>

        <p className="text-sm text-parchment/50">
          Palm shape information was not returned by the backend.
        </p>
      </section>
    )
  }

  return (
    <section className="card">

      <div className="flex items-center gap-3 mb-4">

        <span className="text-2xl">
          ✋
        </span>

        <h3 className="font-display text-2xl text-gold">
          Palm Shape
        </h3>

      </div>

      <h4 className="text-xl text-parchment mb-2">
        {palmShape.shape ||
          'Not available'}
      </h4>

      <p className="text-sm text-parchment/60 leading-relaxed">
        {palmShape.interpretation ||
          'No palm-shape interpretation is available.'}
      </p>

      {palmShape.aspect_ratio && (
        <div className="mt-5 flex justify-between p-3 rounded-lg bg-midnight/40">

          <span className="text-xs text-parchment/50">
            Palm aspect ratio
          </span>

          <span className="text-sm text-gold">
            {palmShape.aspect_ratio}
          </span>

        </div>
      )}

    </section>
  )
}


/* ========================================================= */
/* FINGER STRUCTURE */
/* ========================================================= */

function FingerStructureCard({
  fingerStructure,
}) {

  if (!fingerStructure) {
    return (
      <section className="card">

        <h3 className="font-display text-2xl text-gold mb-3">
          Finger Structure
        </h3>

        <p className="text-sm text-parchment/50">
          Finger structure information was not returned by the backend.
        </p>

      </section>
    )
  }

  return (
    <section className="card">

      <div className="flex items-center gap-3 mb-4">

        <span className="text-2xl">
          ☝️
        </span>

        <h3 className="font-display text-2xl text-gold">
          Finger Structure
        </h3>

      </div>

      <h4 className="text-xl text-parchment mb-2">
        {fingerStructure.structure ||
          'Not available'}
      </h4>

      <p className="text-sm text-parchment/60 leading-relaxed">
        {fingerStructure.interpretation ||
          'No finger-structure interpretation is available.'}
      </p>

      {fingerStructure.method && (
        <div className="mt-5 p-3 rounded-lg bg-midnight/40">

          <p className="text-xs text-parchment/40">
            Analysis method
          </p>

          <p className="text-xs text-lavender mt-1">
            {fingerStructure.method}
          </p>

        </div>
      )}

    </section>
  )
}


/* ========================================================= */
/* INTERPRETATION */
/* ========================================================= */

function InsightReport({
  interpretation,
}) {

  return (
    <section className="card">

      <div className="flex items-center gap-3 mb-5">

        <span className="text-2xl">
          🔮
        </span>

        <h3 className="font-display text-3xl text-gold">
          Reflection & Guidance
        </h3>

      </div>


      {interpretation.summary && (
        <p className="text-base text-parchment/80 leading-relaxed mb-6">
          {interpretation.summary}
        </p>
      )}


      {interpretation.themes?.length > 0 && (

        <div className="mb-6">

          <h4 className="text-sm uppercase tracking-widest text-lavender mb-3">
            Themes
          </h4>

          <div className="flex flex-wrap gap-2">

            {interpretation.themes.map(
              (theme) => (

                <span
                  key={theme}
                  className="px-3 py-1 rounded-full
                             bg-gold/10 border border-gold/20
                             text-xs text-gold"
                >
                  {theme}
                </span>

              )
            )}

          </div>

        </div>

      )}


      {interpretation.personality && (

        <div className="grid md:grid-cols-3 gap-4 mb-7">

          <ReflectionBox
            title="Strength"
            text={
              interpretation
                .personality
                .strength
            }
          />

          <ReflectionBox
            title="Growth Edge"
            text={
              interpretation
                .personality
                .growth_edge
            }
          />

          <ReflectionBox
            title="Reflection"
            text={
              interpretation
                .personality
                .reflection_prompt
            }
          />

        </div>

      )}


      {interpretation.guidance?.length > 0 && (

        <div>

          <h4 className="font-display text-2xl text-gold mb-4">
            Guidance
          </h4>

          <div className="space-y-3">

            {interpretation.guidance.map(
              (item, index) => (

                <div
                  key={`${item.category}-${index}`}
                  className="border-l-2 border-gold/40 pl-4"
                >

                  <p className="text-xs uppercase tracking-widest text-lavender">
                    {item.category}
                  </p>

                  <p className="text-sm text-parchment/70 mt-1">
                    {item.action}
                  </p>

                </div>

              )
            )}

          </div>

        </div>

      )}


      {interpretation.life_trends?.length > 0 && (

        <div className="mt-7">

          <h4 className="font-display text-2xl text-gold mb-4">
            Reflection Timeline
          </h4>

          <div className="grid md:grid-cols-3 gap-4">

            {interpretation.life_trends.map(
              (item) => (

                <div
                  key={item.period}
                  className="p-4 rounded-xl bg-midnight/30
                             border border-lavender/10"
                >

                  <p className="text-xs uppercase tracking-widest text-lavender">
                    {item.period}
                  </p>

                  <p className="text-sm text-gold mt-2">
                    {item.theme}
                  </p>

                  <p className="text-xs text-parchment/50 mt-2 leading-relaxed">
                    {item.guidance}
                  </p>

                </div>

              )
            )}

          </div>

        </div>

      )}


      {interpretation.disclaimer && (

        <div className="mt-7 pt-5 border-t border-lavender/15">

          <p className="text-xs text-parchment/40 leading-relaxed">
            {interpretation.disclaimer}
          </p>

        </div>

      )}

    </section>
  )
}


/* ========================================================= */
/* SMALL REFLECTION BOX */
/* ========================================================= */

function ReflectionBox({
  title,
  text,
}) {

  return (
    <div className="p-5 rounded-xl bg-midnight/30 border border-lavender/10">

      <h4 className="text-sm text-gold font-semibold mb-2">
        {title}
      </h4>

      <p className="text-xs text-parchment/55 leading-relaxed">
        {text || 'No information available.'}
      </p>

    </div>
  )
}


/* ========================================================= */
/* FIND DETECTION */
/* ========================================================= */

function findDetection(
  detections,
  line
) {

  if (!Array.isArray(detections)) {
    return null
  }

  const aliases = {
    life: [
      'life',
      'life_line',
      'life line',
    ],

    head: [
      'head',
      'head_line',
      'head line',
    ],

    heart: [
      'heart',
      'heart_line',
      'heart line',
    ],

    fate: [
      'fate',
      'fate_line',
      'fate line',
    ],

    sun: [
      'sun',
      'sun_line',
      'sun line',
    ],
  }

  return (
    detections.find(
      (detection) =>
        aliases[line]?.includes(
          String(
            detection.line
          ).toLowerCase()
        )
    ) || null
  )
}