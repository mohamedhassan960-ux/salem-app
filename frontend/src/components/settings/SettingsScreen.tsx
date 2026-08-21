import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useUserState } from '../../state/UserStateContext';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import {
  User,
  Cigarette,
  Flame,
  Lock,
  Database,
  Info,
  ShieldCheck,
  LogOut,
  ChevronLeft,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

export interface SettingsScreenProps {
  onBack?: () => void;
  onOpenLogoutDialog: () => void;
}

type ModalKey = 'privacy' | 'data' | 'about' | 'sources' | 'reset_journey' | null;

const MODAL_CONTENT: Record<string, { title: string; body: string[] }> = {
  privacy: {
    title: 'سياسة الخصوصية وسرية البيانات',
    body: [
      'نحن نلتزم بأعلى معايير الأمان والسرية لحماية محادثاتك وسجل تعافيك.',
      'لا يتم بيع أو مشاركة أي بيانات صحية أو سلوكية شخصية مع أي جهات خارجية أو معلنين.',
      'تُستخدم بياناتك فقط لتخصيص نصائح وإرشادات سالم وفق وتيرتك واحتياجك الشخصي.',
    ],
  },
  data: {
    title: 'بياناتك مع سالم',
    body: [
      'ما الذي نحفظه؟ نحفظ ملف التدخين الأساسي (النوع والمعدل)، سجل نوبات الرغبة المسجلة، وحالة المهام اليومية لتسهيل متابعة تقدمك.',
      'لماذا نحفظها؟ لكي لا تضطر لتكرار ظروفك في كل محادثة، ولكي يستطيع سالم تقديم نصائح دقيقة متوافقة مع تقدمك الفعلي.',
      'التحكم في بياناتك: يمكنك إعادة تعيين رحلتك أو طلب حذف حسابك وبياناتك بالكامل في أي وقت.',
    ],
  },
  about: {
    title: 'عن مساعد سالم الطبي',
    body: [
      'سالم هو نظام محادثة وتدخل سلوكي مصمم باللغة العربية لمساعدة المدخنين على التحرر من التبغ خطوة بخطوة.',
      'يجمع سالم بين المعرفة العلمية الموثوقة والدعم السلوكي غير المشروط دون إصدار أي أحكام.',
      'الإصدار 1.0.0 · موجه للبالغين الراغبين في الإقلاع.',
    ],
  },
  sources: {
    title: 'المصادر العلمية المعتمدة (WHO 2024)',
    body: [
      'المصدر الإكلينيكي الأساسي: إرشادات منظمة الصحة العالمية لعلاج الإقلاع عن التبغ لدى البالغين (WHO Clinical Treatment Guideline for Tobacco Cessation in Adults 2024).',
      'تخضع جميع استجابات سالم لتدقيق إكلينيكي صارم لمنع أي معلومات غير مؤكدة علميًا أو ادعاءات مضللة.',
    ],
  },
};

export const SettingsScreen = ({ onBack, onOpenLogoutDialog }: SettingsScreenProps) => {
  const { user } = useAuth();
  const { smokingProfile, resetJourney } = useUserState();
  const [modal, setModal] = useState<ModalKey>(null);

  const handleConfirmReset = () => {
    resetJourney(Date.now());
    setModal(null);
  };

  return (
    <div className="w-full h-full overflow-y-auto p-4 sm:p-6 font-arabic select-none bg-[#F7F9FC]" dir="rtl">
      <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-[#061A3A] tracking-tight">
              الإعدادات والخصوصية
            </h1>
            <p className="text-xs sm:text-sm text-[#5F708C] mt-0.5">
              إدارة حسابك، بيانات رحلة الإقلاع، والتحكم بالخصوصية والمصادر
            </p>
          </div>

          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#FFFFFF] border border-[#D9E2F0] text-xs font-bold text-[#1E3A8A] hover:bg-[#F4F7FB] transition-colors cursor-pointer"
            >
              <ArrowRight className="w-4 h-4" />
              <span>العودة للمحادثة</span>
            </button>
          )}
        </div>

        {/* 1. Account Section */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold text-[#8291A8] px-1">الحساب</span>
          <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-4 sm:p-5 shadow-xs flex items-center justify-between">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#1E3A8A] to-[#2D8BFF] text-white font-bold text-lg flex items-center justify-center shrink-0">
                {user?.name ? user.name.slice(0, 1) : <User className="w-6 h-6" />}
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-[#061A3A]">{user?.name || 'مستخدم سالم'}</span>
                <span className="text-xs text-[#5F708C] mt-0.5">{user?.email || 'user@salem.app'}</span>
                <span className="text-[11px] text-[#2D8BFF] font-semibold mt-0.5">
                  حساب {user?.provider === 'google' ? 'Google' : 'موثق'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Quit Journey Parameters */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold text-[#8291A8] px-1">رحلة الإقلاع</span>
          <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl overflow-hidden shadow-xs divide-y divide-[#D9E2F0]">
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Cigarette className="w-4 h-4 text-[#2D8BFF]" />
                <span className="text-xs sm:text-sm font-medium text-[#061A3A]">نوع التبغ المسجل</span>
              </div>
              <span className="text-xs font-bold text-[#1E3A8A] bg-[#F4F7FB] px-3 py-1 rounded-full border border-[#D9E2F0]">
                {smokingProfile?.tobaccoType || 'سجائر'}
              </span>
            </div>

            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Flame className="w-4 h-4 text-[#2D8BFF]" />
                <span className="text-xs sm:text-sm font-medium text-[#061A3A]">المعدل اليومي السابق</span>
              </div>
              <span className="text-xs font-bold text-[#1E3A8A] bg-[#F4F7FB] px-3 py-1 rounded-full border border-[#D9E2F0]">
                {smokingProfile?.dailyCigarettes || 15} سيجارة / يوم
              </span>
            </div>

            <button
              type="button"
              onClick={() => setModal('reset_journey')}
              className="w-full p-4 flex items-center justify-between hover:bg-[#F4F7FB] transition-colors cursor-pointer text-right"
            >
              <div className="flex items-center gap-3">
                <RotateCcw className="w-4 h-4 text-[#F87171]" />
                <div className="flex flex-col">
                  <span className="text-xs sm:text-sm font-bold text-[#F87171]">إعادة تعيين تاريخ الرحلة</span>
                  <span className="text-[11px] text-[#5F708C]">بدء احتساب أيام التوقف من اليوم دون حذف سجل المحادثات</span>
                </div>
              </div>
              <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
            </button>
          </div>
        </div>

        {/* 3. Privacy & Transparency */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold text-[#8291A8] px-1">الخصوصية وبياناتك</span>
          <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl overflow-hidden shadow-xs divide-y divide-[#D9E2F0]">
            <button
              type="button"
              onClick={() => setModal('data')}
              className="w-full p-4 flex items-center justify-between hover:bg-[#F4F7FB] transition-colors cursor-pointer text-right"
            >
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-[#2D8BFF]" />
                <div className="flex flex-col">
                  <span className="text-xs sm:text-sm font-bold text-[#061A3A]">بياناتك مع سالم (شفافية البيانات)</span>
                  <span className="text-[11px] text-[#5F708C]">شرح مبسط لما نحفظه ولماذا وكيفية حذفه</span>
                </div>
              </div>
              <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
            </button>

            <button
              type="button"
              onClick={() => setModal('privacy')}
              className="w-full p-4 flex items-center justify-between hover:bg-[#F4F7FB] transition-colors cursor-pointer text-right"
            >
              <div className="flex items-center gap-3">
                <Lock className="w-4 h-4 text-[#2D8BFF]" />
                <span className="text-xs sm:text-sm font-bold text-[#061A3A]">سياسة الخصوصية وسرية المعلومات</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
            </button>
          </div>
        </div>

        {/* 4. Trust & Clinical Evidence */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold text-[#8291A8] px-1">الثقة والأدلة الإكلينيكية</span>
          <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl overflow-hidden shadow-xs divide-y divide-[#D9E2F0]">
            <button
              type="button"
              onClick={() => setModal('sources')}
              className="w-full p-4 flex items-center justify-between hover:bg-[#F4F7FB] transition-colors cursor-pointer text-right"
            >
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-4 h-4 text-[#34D399]" />
                <div className="flex flex-col">
                  <span className="text-xs sm:text-sm font-bold text-[#061A3A]">المصادر العلمية المعتمدة (WHO 2024)</span>
                  <span className="text-[11px] text-[#5F708C]">دليل منظمة الصحة العالمية لعلاج التبغ</span>
                </div>
              </div>
              <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
            </button>

            <button
              type="button"
              onClick={() => setModal('about')}
              className="w-full p-4 flex items-center justify-between hover:bg-[#F4F7FB] transition-colors cursor-pointer text-right"
            >
              <div className="flex items-center gap-3">
                <Info className="w-4 h-4 text-[#2D8BFF]" />
                <span className="text-xs sm:text-sm font-bold text-[#061A3A]">عن تطبيق سالم الطبي</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
            </button>
          </div>
        </div>

        {/* 5. Logout */}
        <div className="pt-2">
          <button
            type="button"
            onClick={onOpenLogoutDialog}
            className="w-full p-4 rounded-3xl bg-[#F87171]/10 hover:bg-[#F87171]/20 border border-[#F87171]/30 text-[#B91C1C] font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>تسجيل الخروج من الحساب</span>
          </button>
        </div>

        <p className="text-center text-xs text-[#8291A8] pt-2">
          سالم · الإصدار 1.0.0 · إرشادات WHO الإكلينيكية 2024
        </p>
      </div>

      {/* Info Modals */}
      {modal && modal !== 'reset_journey' && (
        <Modal
          isOpen={true}
          onClose={() => setModal(null)}
          title={MODAL_CONTENT[modal]?.title}
        >
          <div className="flex flex-col gap-3 font-arabic" dir="rtl">
            {MODAL_CONTENT[modal]?.body.map((p, i) => (
              <p key={i} className="text-xs sm:text-sm text-[#061A3A] leading-relaxed">
                {p}
              </p>
            ))}
            <div className="pt-4">
              <Button variant="primary" fullWidth onClick={() => setModal(null)}>
                فهمت ذلك
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Reset Journey Confirmation Modal */}
      {modal === 'reset_journey' && (
        <Modal
          isOpen={true}
          onClose={() => setModal(null)}
          title="إعادة تعيين تاريخ بدء الإقلاع"
          subtitle="هل تريد بدء حساب أيام التوقف من اليوم؟"
        >
          <div className="flex flex-col gap-4 font-arabic" dir="rtl">
            <p className="text-xs sm:text-sm text-[#5F708C] leading-relaxed">
              سيتم تعديل تاريخ التوقف ليبدأ من اليوم مع الحفاظ على جميع محادثاتك ونوبات الرغبة المسجلة السابقة.
            </p>
            <div className="flex gap-2 pt-2">
              <Button variant="danger" fullWidth onClick={handleConfirmReset}>
                تأكيد وبدء الرحلة من اليوم
              </Button>
              <Button variant="ghost" fullWidth onClick={() => setModal(null)}>
                إلغاء
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
