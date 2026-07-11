import { Mesh, Program, Renderer, Triangle } from 'ogl'
import { useEffect, useRef } from 'react'

const vertexShader = `
attribute vec2 uv;
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0.0, 1.0);
}
`

const fragmentShader = `
precision highp float;

uniform float uTime;
uniform vec3 uResolution;
uniform float uSpeed;
uniform float uInnerLines;
uniform float uOuterLines;
uniform float uWarpIntensity;
uniform float uRotation;
uniform float uBrightness;

float hashF(float n) {
  return fract(sin(n * 127.1) * 43758.5453123);
}

float smoothNoise(float x) {
  float i = floor(x);
  float f = fract(x);
  float u = f * f * (3.0 - 2.0 * f);
  return mix(hashF(i), hashF(i + 1.0), u);
}

float displaceA(float coord, float t) {
  return sin(coord * 2.123) * 0.2
    + sin(coord * 3.234 + t * 4.345) * 0.1
    + sin(coord * 0.589 + t * 0.934) * 0.5;
}

float displaceB(float coord, float t) {
  return sin(coord * 1.345) * 0.3
    + sin(coord * 2.734 + t * 3.345) * 0.2
    + sin(coord * 0.189 + t * 0.934) * 0.3;
}

vec2 rotate2D(vec2 point, float angle) {
  float c = cos(angle);
  float s = sin(angle);
  return vec2(point.x * c - point.y * s, point.x * s + point.y * c);
}

void main() {
  vec2 coords = gl_FragCoord.xy / uResolution.xy;
  coords = rotate2D(coords * 2.0 - 1.0, uRotation);

  float halfTime = uTime * uSpeed * 0.5;
  float fullTime = uTime * uSpeed;
  vec2 fieldA = vec2(
    coords.x + displaceA(coords.y, halfTime) * uWarpIntensity,
    coords.y - displaceA(coords.x * cos(fullTime) * 1.235, halfTime) * uWarpIntensity
  );
  vec2 fieldB = vec2(
    coords.x + displaceB(coords.y, halfTime) * uWarpIntensity,
    coords.y - displaceB(coords.x * sin(fullTime) * 1.235, halfTime) * uWarpIntensity
  );
  vec2 blended = mix(fieldA, fieldB, 0.5);

  float edge = smoothstep(1.0, 0.45, abs(blended.y));
  float tileCount = mix(uOuterLines, uInnerLines, edge);
  float scaledY = blended.y * tileCount;
  float noise = smoothNoise(abs(scaledY));
  float ridge = pow(max(0.0, cos(2.0 * (noise - blended.x))), 5.0);
  float lines = pow(max(fract(scaledY), fract(-scaledY)), 2.0)
    + pow(max(fract(scaledY), fract(-scaledY)), 4.0);
  float pattern = edge * lines + ridge * 0.35;
  vec3 white = vec3(pattern * uBrightness);
  gl_FragColor = vec4(white, clamp(length(white) * 1.6, 0.0, 1.0));
}
`

interface LineWavesProps {
  speed?: number
  brightness?: number
}

export function LineWaves({ speed = 0.16, brightness = 0.26 }: LineWavesProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let animationFrameId: number | undefined
    let canvas: HTMLCanvasElement | undefined
    let loseContext: (() => void) | undefined

    try {
      const renderer = new Renderer({ alpha: true, premultipliedAlpha: false })
      const gl = renderer.gl
      canvas = gl.canvas
      gl.clearColor(0, 0, 0, 0)

      const program = new Program(gl, {
        vertex: vertexShader,
        fragment: fragmentShader,
        uniforms: {
          uTime: { value: 0 },
          uResolution: { value: [1, 1, 1] },
          uSpeed: { value: speed },
          uInnerLines: { value: 22 },
          uOuterLines: { value: 26 },
          uWarpIntensity: { value: 0.8 },
          uRotation: { value: (-45 * Math.PI) / 180 },
          uBrightness: { value: brightness },
        },
      })
      const mesh = new Mesh(gl, { geometry: new Triangle(gl), program })

      const resize = () => {
        renderer.setSize(container.offsetWidth, container.offsetHeight)
        program.uniforms.uResolution.value = [gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height]
      }
      const update = (time: number) => {
        program.uniforms.uTime.value = time * 0.001
        renderer.render({ scene: mesh })
        animationFrameId = window.requestAnimationFrame(update)
      }

      container.appendChild(canvas)
      resize()
      window.addEventListener('resize', resize)
      animationFrameId = window.requestAnimationFrame(update)
      loseContext = () => gl.getExtension('WEBGL_lose_context')?.loseContext()

      return () => {
        if (animationFrameId) window.cancelAnimationFrame(animationFrameId)
        window.removeEventListener('resize', resize)
        if (canvas?.parentElement === container) container.removeChild(canvas)
        loseContext?.()
      }
    } catch {
      return undefined
    }
  }, [brightness, speed])

  return <div ref={containerRef} className="line-waves" aria-hidden="true" />
}
