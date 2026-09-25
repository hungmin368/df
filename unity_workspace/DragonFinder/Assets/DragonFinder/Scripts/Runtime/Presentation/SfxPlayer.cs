using System;
using UnityEngine;

namespace DragonFinder.Runtime.Presentation
{
    public sealed class SfxPlayer : MonoBehaviour
    {
        private AudioSource source;
        private AudioClip click;
        private AudioClip caught;
        private AudioClip missed;
        private AudioClip win;
        private AudioClip lose;

        public bool Enabled { get; set; } = true;

        private void Awake()
        {
            source = gameObject.AddComponent<AudioSource>();
            source.playOnAwake = false;
            click = CreateTone("Click", 440, 0.06f, 0.08f);
            caught = CreateTone("Caught", 740, 0.12f, 0.12f);
            missed = CreateTone("Missed", 180, 0.12f, 0.1f);
            win = CreateTone("Win", 920, 0.24f, 0.12f);
            lose = CreateTone("Lose", 120, 0.28f, 0.1f);
        }

        public void PlayClick() => Play(click);
        public void PlayCaught() => Play(caught);
        public void PlayMissed() => Play(missed);
        public void PlayWin() => Play(win);
        public void PlayLose() => Play(lose);

        private void Play(AudioClip clip)
        {
            if (Enabled && clip != null)
            {
                source.PlayOneShot(clip);
            }
        }

        private static AudioClip CreateTone(string name, float frequency, float duration, float volume)
        {
            const int sampleRate = 44100;
            int sampleCount = Mathf.CeilToInt(sampleRate * duration);
            var samples = new float[sampleCount];
            for (int i = 0; i < sampleCount; i++)
            {
                float fade = 1f - i / (float)sampleCount;
                samples[i] = Mathf.Sin(2f * Mathf.PI * frequency * i / sampleRate) * volume * fade;
            }

            AudioClip clip = AudioClip.Create(name, sampleCount, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
