import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ArrowRight, User, Globe, Moon, Lock, Database, Info, ShieldCheck, LogOut, ChevronLeft, X } from 'lucide-react';

export interface SettingsScreenProps {
  onBack: () => void;
  onOpenLogoutDialog: () => void;
}

type ModalKey = 'privacy' | 'data' | 'about' | 'sources' | null;

const MODAL_CONTENT: Record<NonNullable<ModalKey>, { title: string; body: string[] }> = {
  privacy: {
    title: 'سياسة الخصوصية',
    body: [
      'نستخدم بيانات الحساب والمحادثات لتقديم تجربة المساعد الطبي وفق إعدادات الخدمة.',
      'لا نشارك أي بيانات صحية شخصية مع أطراف خارجية أو جهات دعائية.',
    ],
  },
  data: {
    title: 'البيانات والمحادثات',
    body: [
      'ترتبط المحادثات بحسابك لتسهيل استرجاع خطة الإقلاع ومتابعة تقدمك.',
      'يمكنك بدء محادثة جديدة أو إدارة الجلسات في أي وقت.',
    ],
  },
  about: {
    title: 'عن تطبيق سالم الطبي',
    body: [
      'سالم مساعد صحي وسلوكي متقدم للإقلاع عن التدخين، مستند لأحدث أدلة منظمة الصحة العالمية (WHO 2024).',
      'سالم يقدم نصائح مبسطة وداعمة مع الالتزام الصارم بالسلامة والأدلة الطبية المعتمدة.',
    ],
  },
  sources: {
    title: 'المصادر والمنهجية',
    body: [
      'المصدر الطبي: دليل منظمة الصحة العالمية الإكلينيكي للإقلاع عن التبغ لدى البالغين (WHO 2024).',
      'تخضع جميع إرشادات سالم لتدقيق إكلينيكي صارم لضمان سلامة التوصيات الطبية.',
    ],
  },
};

export const SettingsScreen = ({ onBack, onOpenLogoutDialog }: SettingsScreenProps) => {
  const { user } = useAuth();
  const [appearance, setAppearance] = useState<'dark' | 'light' | 'system'>('dark');
  const [modal, setModal] = useState<ModalKey>(null);

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <div
        className="shrink-0 bg-slate-900 border-b border-slate-800/80 px-4 flex items-center gap-3"
        style={{ paddingTop: 'calc(0.875rem + var(--sat))', paddingBottom: '0.875rem' }}
      >
        <button
          type="button"
          onClick={onBack}
          aria-label="الرجوع إلى المحادثة"
          className="w-9 h-9 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors cursor-pointer"
        >
          <ArrowRight className="w-5 h-5" />
        </button>
        <h1 className="text-base font-bold text-white">الإعدادات</h1>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-5 flex flex-col gap-5" style={{ paddingBottom: 'calc(1.5rem + var(--sab))' }}>

          {/* Account */}
          <Section label="الحساب">
            <div className="flex items-center gap-3.5 px-4 py-3.5">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-sky-500 to-blue-700 flex items-center justify-center text-white font-bold text-base border border-sky-400/30 shrink-0">
                {user?.name ? user.name.slice(0, 1) : <User className="w-5 h-5" />}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-semibold text-white truncate">{user?.name || 'محمد حسن'}</span>
                <span className="text-xs text-slate-400 truncate">{user?.email || 'mohamed.hassan@gmail.com'}</span>
                <span className="text-[10px] text-sky-400 font-medium mt-0.5">{user?.provider || 'Google Account'}</span>
              </div>
            </div>
          </Section>

          {/* App preferences */}
          <Section label="التطبيق">
            <SettingsRow
              icon={<Globe className="w-4 h-4 text-sky-400" />}
              label="اللغة"
              trailing={<span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded-lg">العربية</span>}
            />
            <div className="border-t border-slate-800/60" />
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
                <Moon className="w-4 h-4 text-sky-400" />
                <span>المظهر</span>
              </div>
              <div className="flex items-center bg-slate-950 rounded-lg p-0.5 border border-slate-800 text-[11px]">
                {(['dark', 'light', 'system'] as const).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setAppearance(opt)}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                      appearance === opt ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {opt === 'dark' ? 'داكن' : opt === 'light' ? 'فاتح' : 'النظام'}
                  </button>
                ))}
              </div>
            </div>
          </Section>

          {/* Privacy */}
          <Section label="الخصوصية والبيانات">
            <SettingsButton
              icon={<Lock className="w-4 h-4 text-sky-400" />}
              label="سياسة الخصوصية"
              onClick={() => setModal('privacy')}
            />
            <div className="border-t border-slate-800/60" />
            <SettingsButton
              icon={<Database className="w-4 h-4 text-sky-400" />}
              label="البيانات والمحادثات"
              onClick={() => setModal('data')}
            />
          </Section>

          {/* About */}
          <Section label="عن التطبيق">
            <SettingsButton
              icon={<Info className="w-4 h-4 text-sky-400" />}
              label="عن تطبيق سالم الطبي"
              onClick={() => setModal('about')}
            />
            <div className="border-t border-slate-800/60" />
            <SettingsButton
              icon={<ShieldCheck className="w-4 h-4 text-sky-400" />}
              label="المصادر والمنهجية الطبية"
              onClick={() => setModal('sources')}
            />
          </Section>

          {/* Logout */}
          <div className="rounded-xl border border-rose-900/40 overflow-hidden">
            <button
              type="button"
              onClick={onOpenLogoutDialog}
              className="w-full flex items-center gap-2.5 px-4 py-3.5 text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer text-xs font-semibold"
            >
              <LogOut className="w-4 h-4" />
              <span>تسجيل الخروج</span>
            </button>
          </div>

          <p className="text-center text-[11px] text-slate-600">
            سالم · الإصدار 1.0.0 · WHO 2024
          </p>
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-5 bg-black/70 backdrop-blur-sm"
          dir="rtl"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col max-h-[70vh]">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">{MODAL_CONTENT[modal].title}</h3>
              <button
                type="button"
                onClick={() => setModal(null)}
                aria-label="إغلاق"
                className="w-8 h-8 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
              {MODAL_CONTENT[modal].body.map((p, i) => (
                <p key={i} className="text-xs text-slate-300 leading-relaxed">{p}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ── Small helper components ──────────────────
const Section = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="flex flex-col gap-2">
    <span className="text-[10px] font-bold text-slate-500 px-1 tracking-wider uppercase">{label}</span>
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 overflow-hidden">
      {children}
    </div>
  </div>
);

const SettingsRow = ({
  icon,
  label,
  trailing,
}: {
  icon: React.ReactNode;
  label: string;
  trailing?: React.ReactNode;
}) => (
  <div className="flex items-center justify-between px-4 py-3">
    <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
      {icon}
      <span>{label}</span>
    </div>
    {trailing}
  </div>
);

const SettingsButton = ({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-800/50 transition-colors cursor-pointer"
  >
    <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
      {icon}
      <span>{label}</span>
    </div>
    <ChevronLeft className="w-4 h-4 text-slate-500" />
  </button>
);
