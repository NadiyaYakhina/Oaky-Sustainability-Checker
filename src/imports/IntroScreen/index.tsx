import svgPaths from "./svg-sjri9acsnj";
import imgDefaultOaky from "./10b6c7e91cb1a74dd5a00fbbe3c03174575c0ec3.png";

function CancelIcon() {
  return <div className="absolute inset-[1.59%_3.88%_93.83%_85.33%]" data-name="Cancel Icon" />;
}

function InfoIcon() {
  return <div className="absolute inset-[1.55%_18.23%_93.87%_70.99%]" data-name="Info Icon" />;
}

function Group() {
  return (
    <div className="absolute inset-[78.94%_-17.95%_18.87%_112.72%]" data-name="Group">
      <svg className="absolute block inset-0 size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 180.289 178.116">
        <g id="Group">
          <path d={svgPaths.p13cd1b00} fill="var(--fill-0, #020202)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function CloseIcon() {
  return <div className="absolute left-[2925px] size-[358px] top-[133px]" data-name="Close Icon" />;
}

function StartButton() {
  return (
    <div className="absolute contents left-[814px] top-[5125px]" data-name="Start Button">
      <div className="absolute bg-[#7db493] h-[432px] left-[814px] rounded-[117.722px] top-[5125px] w-[1801px]" data-name="Button Background" />
      <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Instrument_Serif:Regular',sans-serif] h-[337px] leading-[normal] left-[calc(50%+0.5px)] not-italic text-[300px] text-black text-center top-[5125px] w-[1065px]">Start</p>
    </div>
  );
}

export default function IntroScreen() {
  return (
    <div className="bg-[#f4f4f4] relative size-full" data-name="Intro Screen">
      <div className="-translate-x-1/2 absolute h-[2756px] left-1/2 top-[2369px] w-[4028px]">
        <svg className="absolute block inset-0 size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 4028 2756">
          <ellipse cx="2014" cy="1378" fill="url(#paint0_radial_1_278)" id="Ellipse 2" rx="2014" ry="1378" />
          <defs>
            <radialGradient cx="0" cy="0" gradientTransform="translate(2014 1378) rotate(90) scale(1378 2014)" gradientUnits="userSpaceOnUse" id="paint0_radial_1_278" r="1">
              <stop stopColor="#EACF9A" />
              <stop offset="0.216356" stopColor="#EFDBB4" stopOpacity="0.745182" />
              <stop offset="1" stopColor="white" stopOpacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div className="absolute h-[8172px] left-[-32px] top-[-9.5px] w-[3494px]" data-name="Untitled_Artwork-5 1">
        <svg className="absolute block inset-0 size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
          <g id="Untitled_Artwork-5 1" />
        </svg>
      </div>
      <div className="-translate-x-1/2 absolute h-[423px] left-[calc(50%+0.5px)] top-[4166px] w-[3181px]">
        <svg className="absolute block inset-0 size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 3181 423">
          <ellipse cx="1590.5" cy="211.5" fill="url(#paint0_radial_1_271)" id="Ellipse 1" rx="1590.5" ry="211.5" />
          <defs>
            <radialGradient cx="0" cy="0" gradientTransform="translate(1590.5 211.5) scale(1590.5 211.5)" gradientUnits="userSpaceOnUse" id="paint0_radial_1_271" r="1">
              <stop stopColor="#9A8A6A" />
              <stop offset="0.47117" stopColor="#EDE4D1" stopOpacity="0.769005" />
              <stop offset="0.82214" stopColor="#F4EDE1" stopOpacity="0.5" />
              <stop offset="1" stopColor="white" stopOpacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div className="absolute bg-[#f0e8d8] h-[431.647px] left-[2364px] rounded-[117.722px] top-[102px] w-[1001.313px]" data-name="Icon Background" />
      <CancelIcon />
      <InfoIcon />
      <Group />
      <CloseIcon />
      <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Instrument_Serif:Regular',sans-serif] h-[1040px] leading-[normal] left-1/2 not-italic text-[200px] text-black text-center top-[1181px] w-[2460px]">Hi there, my name is Oakly and I’m here to help you check if the clothes you’re buying are eco-friendly!</p>
      <div className="-translate-x-1/2 absolute h-[2293px] left-1/2 top-[2221px] w-[1374px]" data-name="Default Oaky">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <img alt="" className="absolute h-[212.23%] left-[-23.53%] max-w-none top-[-45.8%] w-[354.33%]" src={imgDefaultOaky} />
        </div>
      </div>
      <StartButton />
    </div>
  );
}